from .state_stake import StateStaking
from .state_pool_player import StatePool, StatePlayer

# 整个游戏的处理器、负责单次投注的完整处理过程
class StateSimulating:
    def __init__(self, stake_level, stake_mode, stake_rounds, rng, cfg):
        # 外部传入
        self.stake_level = stake_level  # 当前投注档位
        self.stake_mode = stake_mode  # 1、2、3 分别对应普通投注、购买免费、scatter增幅
        self.stake_rounds = stake_rounds  # 需要模拟投注的局数
        self.rng = rng  # RNG实例
        self.cfg = cfg  # 配置数据
        # stake_mode guardrail
        if self.stake_mode not in (1, 2, 3):
            raise ValueError(f"Invalid stake_mode={self.stake_mode}, expected 1/2/3")
        # 内部初始化
        self.pool = StatePool(self.cfg)
        self.player = StatePlayer(self.cfg)
        self.missing_stake = 0  # 普通模式下连续失败局数、初始为0
        self.staking_history = []  # 记录本次投注的所有局数据
        self.restake_mini_protect = 0
        self.restake_odds_range = 0
        self.stake_number = 1  # 当前投注编号、初始为1

        self.excel_rounding_history = []  # 收集所有轮次历史
        self.excel_rolling_history = []   # 收集所有掉落历史

        stake_cost_ratio = self.cfg['cost_ratio'][self.stake_mode - 1]
        self.total_stake = self.stake_level * stake_cost_ratio

    # 模拟单次投注的完整过程
    def process_single_stake(self):
        control_level = self.pool.get_control_level(self.stake_level)

        # control_level guardrail
        control_levels = self.cfg["control_levels"]
        if control_level not in control_levels:
            raise KeyError(
                f"Invalid control_level={control_level}. "
                f"Available={sorted(control_levels.keys())}"
            )

        control_data_root = control_levels[control_level]

        # stake_mode guardrail
        if self.stake_mode not in control_data_root:
            raise KeyError(
                f"Config missing stake_mode={self.stake_mode} "
                f"under control_level={control_level}. "
                f"Available={sorted(control_data_root.keys())}"
            )

        self.control_data = control_data_root[self.stake_mode]
        self.staking = StateStaking(self.stake_number, self.stake_mode, self.control_data, self.rng, self.cfg)
        self.staking.process_several_rounds()

    # 模拟多次投注的完整过程
    def process_several_stakes(self, progress_callback=None):
        while self.evaluate_staking():
            # 每次新的stake开始时，重置重摇计数器
            stake_restake_mini_protect = 0  # 当前stake的mini_protect重摇次数
            stake_restake_odds_range = 0    # 当前stake的odds_range重摇次数

            while True:
                while True:
                    self.process_single_stake()
                    if not self.evaluate_mini_protect():
                        break
                    stake_restake_mini_protect += 1
                if not self.evaluate_total_odds_range():
                    break
                stake_restake_odds_range += 1

            # 在记录数据前，先更新实例变量为当前stake的值
            self.restake_mini_protect = stake_restake_mini_protect
            self.restake_odds_range = stake_restake_odds_range

            # 数据记录 
            self.record_stake_data()
            # 状态推进
            self.process_simulate_state()

            # 更新进度条
            if progress_callback:
                progress_callback(1)

    # 数据记录
    def record_stake_data(self):
        self.staking_history.append({
            'stake_level': self.stake_level,
            'stake_mode': self.stake_mode,
            'total_stake': self.total_stake,
            'stake_number': self.stake_number,
            'basic_odds': self.staking.basic_odds,
            'free_odds': self.staking.free_odds,
            'total_odds': self.staking.total_odds_this_stake,
            'rounding_history': self.staking.rounding_history,

            # 水池线
            'waterline': (self.pool.get_target_pool(self.stake_level) or {}).get('waterline', 0),
            #难度档位
            'control_level': self.pool.get_control_level(self.stake_level),
            
            'missing_stake': self.missing_stake,
            'restake_mini_protect': self.restake_mini_protect,
            'restake_odds_range': self.restake_odds_range,
        })

        if hasattr(self.staking, 'rounding_history'):
            self.excel_rounding_history.extend(self.staking.rounding_history)
        
        # 收集当前stake的所有roll数据
        for rounding_data in self.staking.rounding_history:
            if 'rolling_history' in rounding_data:
                self.excel_rolling_history.extend(rounding_data['rolling_history'])

    # 得分结算与状态推进
    def process_simulate_state(self):
        # 基础状态更新
        self.stake_number += 1
        self.stake_rounds -= 1
        if self.staking.total_odds_this_stake == 0:
            self.missing_stake += 1
        else:
            self.missing_stake = 0
        # 玩家状态更新
        self.player.update_after_round(
            self.stake_level,
            self.stake_mode,
            self.staking.basic_odds,
            self.staking.free_odds
        )
        # 水池状态更新
        self.pool.update_waterline(
            self.stake_level,
            self.stake_mode,
            self.staking.total_odds_this_stake,
        )

    # 评价何时继续staking：若仍有剩余投注局数，则继续
    def evaluate_staking(self):
        if self.stake_rounds > 0:
            return True
        return False
    
    # 重摇策略相关
    # 1.total_odds_range判断方法(仅限中了free之后的多rounds合计、所以round_mode固定为2)
    def evaluate_total_odds_range(self):
        total_odds_range = self.control_data['total_odds_range']
        if total_odds_range[0] <= self.staking.total_odds_this_stake <= total_odds_range[1]:
            return False
        else:
            return True
        
    # mini_protect判断方法(不论模式、所有stake都适用)
    def evaluate_mini_protect(self):
        config_mini_protect = self.control_data[1]['mini_protect']
        if self.missing_stake >= config_mini_protect[0]:
            if self.staking.total_odds_this_stake == 0:  # 只有在没中奖时才触发保护
                if self.rng.uniform(0, 100) <= config_mini_protect[1]:
                    return True
        return False