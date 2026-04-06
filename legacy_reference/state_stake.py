from src.core.state_round import StateRounding

class StateStaking:
    def __init__(self, stake_number, stake_mode, stake_control_data, rng, cfg):
        # 外部传入
        self.stake_number = stake_number
        self.stake_mode = stake_mode
        self.stake_control_data = stake_control_data
        self.rng = rng
        self.cfg = cfg
        # 内部初始化
        self.round_number = 1  # 当前局数、初始为1
        self.round_mode = 1  # 1、2 分别表示普通模式、免费模式；初始值为1表示总是以普通模式开始
        self.remaining_rounds = 1  # 剩余摇奖局数、初始为1
        self.global_multiplier = 0  # 免费模式下全局倍率、初始为0
        self.succeed_rounds_free = 0  # 免费模式下连续赢局数、初始为0
        self.total_odds_this_stake = 0  # 本次stake的总赔率
        self.free_game_missing_rounds = 0  # 免费模式连续失败局数、初始为0
        self.rounding_history = []  # 记录本次stake下所有round的综合数据
        self.reround_mini_protect = 0
        self.reround_odds_range = 0
        self.basic_odds = 0  # 普通模式下的总赔率
        self.free_odds = 0  # 免费模式下的总赔率

    # 循环单次下注的多局游戏、直到不再需要继续
    def process_single_round(self):
        round_control_data = self.stake_control_data[self.round_mode]
        self.rounding = StateRounding(self.stake_number, self.round_number, round_control_data, self.stake_mode, self.round_mode, self.global_multiplier, self.succeed_rounds_free, self.rng, self.cfg)
        self.rounding.process_several_rolls()
        self.rounding.process_multi_pattern()
        self.rounding.process_scatter_pattern()
        self.rounding.setting_round()

    def process_several_rounds(self):
        while True:
            while True:
                while True:
                    self.process_single_round()
                    if not self.evaluate_mini_protect():
                        break
                    self.reround_mini_protect += 1
                if not self.evaluate_odds_range():
                    break
                self.reround_odds_range += 1
            # 数据记录
            self.record_round_data()
            # 得分结算与状态推进
            self.process_stake_state()
            if not self.evaluate_rounding():
                break

    # 数据记录
    def record_round_data(self):
        self.rounding_history.append({
            'stake_number': self.stake_number,
            'round_number': self.round_number,
            'game_mode': 'Basic' if self.round_mode == 1 else 'Free',
            'regular_odds': self.rounding.regular_odds,
            'basic_odds': self.rounding.basic_odds,
            'multi_odds': self.rounding.multi_odds,
            'scatter_odds': self.rounding.scatter_odds,
            'total_odds': self.rounding.total_odds,
            'pattern_multiplier': self.rounding.pattern_multiplier,
            'multi_count': self.rounding.multi_count,
            'scatter_count': self.rounding.scatter_count,
            'bonus_rounds_awarded': self.rounding.bonus_rounds_awarded,
            'global_multiplier': self.rounding.global_multiplier,
            'matrix_end': self.rounding.matrix,
            'rolling_history': self.rounding.rolling_history,

            'free_game_missing_rounds': self.free_game_missing_rounds,
            'reround_odds_range': self.reround_odds_range,
            'reround_mini_protect': self.reround_mini_protect,
        })

    # 得分结算与状态推进
    def process_stake_state(self):
        # 得分结算
        self.total_odds_this_stake += self.rounding.total_odds
        if self.round_mode == 1:
            self.basic_odds += self.rounding.total_odds
        else:
            self.free_odds += self.rounding.total_odds
        
        # round次数更新
        self.remaining_rounds -= 1
        self.round_number += 1
        self.remaining_rounds += self.rounding.bonus_rounds_awarded

        # 模式变更与策略参数更新
        if self.round_mode == 1 and self.rounding.bonus_rounds_awarded > 0:
            self.round_mode = 2
        # 若本局为免费模式、则更新免费模式相关状态
        if self.round_mode == 2:
            if self.rounding.total_odds == 0:
                self.free_game_missing_rounds += 1
            else:
                # 赢局则连续失败局数归0
                self.free_game_missing_rounds = 0
                # 如果本round有倍率图案、则更新全局倍率
                if self.rounding.pattern_multiplier > 0:
                    self.global_multiplier += self.rounding.pattern_multiplier
                    # 赢局则连续赢局数+1
                    self.succeed_rounds_free += 1

    # 评价何时继续rounding
    def evaluate_rounding(self):
        if self.remaining_rounds > 0:
            return True
        return False
        
    # 2.odds_range判断方法
    def evaluate_odds_range(self):
        odds_range = self.stake_control_data[self.round_mode]['odds_range']
        if odds_range[0] <= self.rounding.total_odds <= odds_range[1]:
            return False
        else:
            return True

    # 3.mini_protect判断方法(free模式下)
    def evaluate_mini_protect(self):
        config_mini_protect = self.stake_control_data[2]['mini_protect']
        if self.round_mode == 2:
            if self.free_game_missing_rounds >= config_mini_protect[0]:
                if self.total_odds_this_stake == 0:  # 只有在没中奖时才触发保护
                    if self.rng.random() <= config_mini_protect[1]:
                        return True
        return False