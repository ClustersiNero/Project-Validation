# 水池状态、用水池承载大盘输赢、并以水位线来进行难度档位的选择、以此实现负反馈调控
class StatePool:
    # 初始化全部水池、并赋予初始 waterline（水位线）
    def __init__(self, cfg):
        self.pools = {}
        self.cfg = cfg
        # 为了保持顺序，最好先对 pool_id 进行排序
        for pool_id in sorted(self.cfg['pool_data'].keys()):
            pool_data = self.cfg['pool_data'][pool_id].copy() # 使用副本以避免修改原始配置
            pool_data['waterline'] = pool_data['waterline_init']
            self.pools[pool_id] = pool_data

    def get_target_pool(self, stake_level):
        for pool_id, pool_data in self.pools.items():
            stake_range = pool_data['stake_range']
            if stake_range[0] <= stake_level < stake_range[1]:
                return pool_data
        return None

    # 根据被调用的水池的当前水位线确定难度档位、直接返回难度档位编号（99/100/101)
    def get_control_level(self, stake_amount):
        target_pool = self.get_target_pool(stake_amount)
        if not target_pool:
            min_level = min(
                min(pool['control_level']) for pool in self.pools.values() if 'control_level' in pool and pool['control_level']
            )
            return min_level

        # 根据找到的水池的当前水位线确定难度档位
        waterline = target_pool['waterline']
        water_levels = target_pool['water_level']
        control_levels = target_pool['control_level']

        # 遍历水位阈值，找到对应的难度档位
        for i, level_threshold in enumerate(water_levels):
            if waterline <= level_threshold:
                # 容错处理：如果control_levels数量少于water_levels数量，则返回最小的难度档位
                if i < len(control_levels):
                    return control_levels[i]
                else:
                    return control_levels[0]

        # 如果如果找不到对应的区间，返回最低的难度档位
        return control_levels[-1]

    # 根据投注档位、投注模式确定投注金额、根据投注金额*抽水比例计算流入、根据流入赔付金额、流入金额计算水池变化
    def update_waterline(self, stake_level, stake_mode, payout_odds):
        target_pool = self.get_target_pool(stake_level)
        if not target_pool:
            return
        # 获取stake档位对应归一投注额的比例
        stake_cost_ratio = self.cfg['cost_ratio'][stake_mode - 1]
        # 计算归一投注额
        stake_amount = stake_level * stake_cost_ratio

        # 归一化流入
        inflow = stake_amount * (1 - target_pool['tax_ratio'])
        # 归一化流出
        outflow = payout_odds * stake_level
        # 归一化水池变化
        net_change = inflow - outflow
        # 更新水位线(实际金额变化 = 归一化金额变化 * 归一投注额比例)
        target_pool['waterline'] += net_change

# 玩家状态、主要用作数据统计
class StatePlayer:
    def __init__(self, cfg):
        self.cfg = cfg
        self.stake_amount = 0
        self.win_amount_all = 0
        self.win_amount_basic = 0
        self.win_amount_free = 0
        self.stake_amount_total = 0
        self.win_amount_all_total = 0
        self.win_amount_basic_total = 0
        self.win_amount_free_total = 0

        self.rounds_stake = 0
        self.rounds_basic = 0
        self.rounds_free = 0
        self.rounds_total_win = 0
    
    def reset_round_data(self):
        self.win_amount_all = 0
        self.win_amount_basic = 0
        self.win_amount_free = 0

    def update_after_round(self, stake_level, stake_mode, win_odds_basic, win_odds_free):
        # 先清除遗留数据
        self.reset_round_data()
        # 先根据stake_level获取对应的水池
        target_pool = StatePool(self.cfg).get_target_pool(stake_level)

        # 获取stake档位对应归一投注额的比例
        stake_cost_ratio = self.cfg['cost_ratio'][stake_mode - 1] if target_pool else 1

        # 更新金额
        # 投注
        self.stake_amount = stake_level * stake_cost_ratio
        self.stake_amount_total += self.stake_amount

        # 赢取
        # basic
        if win_odds_basic > 0:
            self.win_amount_basic = win_odds_basic * stake_level
            self.win_amount_basic_total += self.win_amount_basic
            self.rounds_basic += 1
        # free
        if win_odds_free > 0:
            self.win_amount_free = win_odds_free * stake_level
            self.win_amount_free_total += self.win_amount_free
            self.rounds_free += 1
        # all
        self.win_amount_all = self.win_amount_basic + self.win_amount_free
        self.win_amount_all_total += self.win_amount_all

        # 更新总赢取轮数
        if win_odds_basic + win_odds_free > 0:
            self.rounds_total_win += 1

        # 更新总轮数
        self.rounds_stake += 1

    def calculate_rates_and_rtp(self):
        self.rate_basic = self.rounds_basic / self.rounds_stake if self.rounds_stake > 0 else 0
        self.rate_free = self.rounds_free / self.rounds_stake if self.rounds_stake > 0 else 0
        self.rate_total_win = self.rounds_total_win / self.rounds_stake if self.rounds_stake > 0 else 0

        self.rtp_basic = self.win_amount_basic_total / self.stake_amount_total if self.stake_amount_total > 0 else 0
        self.rtp_free = self.win_amount_free_total / self.stake_amount_total if self.stake_amount_total > 0 else 0
        self.rtp_total = self.win_amount_all_total / self.stake_amount_total if self.stake_amount_total > 0 else 0

