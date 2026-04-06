from src.core.state_roll import StateRolling

class StateRounding:
    def __init__(self, stake_number, round_number, round_control_data, stake_mode, round_mode, global_multiplier, succeed_rounds_free, rng, cfg):
        # 外部传入
        self.stake_number = stake_number
        self.round_number = round_number
        self.round_control_data = round_control_data
        self.stake_mode = stake_mode
        self.round_mode = round_mode  # 1: basic 2: free
        self.succeed_rounds_free = succeed_rounds_free
        self.global_multiplier = global_multiplier  # free模式下的全局倍率
        self.rng = rng
        self.cfg = cfg
        # 内部初始化
        self.roll_number = 1
        self.matrix = [[0 for _ in range(5)] for _ in range(6)]
        self.roll_mode = 1  # 1: 初次掉落 2: 补位掉落
        self.rolling_history = []  # 记录每次滚动的图案矩阵、是否中奖、得分
        self.regular_odds = 0  # 普通图案得分

    # 评价何时继续rolling：若图案矩阵中仍有空位（0），则继续滚动
    def evaluate_rolling(self, matrix):
        for row in range(5):
            for col in range(6):
                symbol = matrix[col][row]
                if symbol == 0:
                    return True
        return False
    
    # 获取实体轴编号
    def get_reel_set_id(self):
        key = f'roll_mode_{self.roll_mode}'
        reel_set_select_weight = self.round_control_data[key]
        self.reel_set_id = self.rng.choices(range(len(reel_set_select_weight)), weights=reel_set_select_weight)[0] + 1
    
    # 循环单局游戏的多次图案掉落&消除补位循环、直到不再需要继续、输出图案矩阵、multi&scatter数量；以及整个循环过程中的累计普通图案得分、
    def process_several_rolls(self):
        while self.evaluate_rolling(self.matrix):
            self.get_reel_set_id()
            self.rolling = StateRolling(self.reel_set_id, self.matrix, self.rng, self.cfg)
            self.rolling.patch_matrix()
            self.rolling.process_regular_pattern()
            # 数据记录
            self.rolling_history.append({
                'stake_number': self.stake_number,
                'round_number': self.round_number,
                'roll_number': len(self.rolling_history) + 1,
                'reel_set_id': self.rolling.reel_set_id,
                'matrix': self.rolling.matrix,
                'regular_odds': self.rolling.regular_odds,
                'winning_symbols_details': self.rolling.winning_symbols_details,
            })
            # 更新状态
            self.regular_odds += self.rolling.regular_odds
            self.matrix = self.rolling.matrix
            self.roll_mode = 2  # 后续均为补位掉落

    # 处理multi图案
    def process_multi_pattern(self):
        # 统计multi图案数量
        self.multi_count = 0
        for col in range(6):
            for row in range(5):
                if self.matrix[col][row] == 11:  # multi图案ID
                    self.multi_count += 1

        # 若有multi图案、为其赋值
        multi_data = self.cfg['pattern_multi_data']
        odds_range = multi_data['odd_range']
        color_keys = multi_data['key']
        weight_root = multi_data['weight']

        # 根据1.是否中奖、2.投注模式：1or2or3；3.免费环境累计中奖次数；选择对应的multi权重表
        has_win = self.regular_odds > 0
        # 1. 是否中奖
        if not has_win:
            # 未中奖时，直接使用 'fail' 对应的权重列表
            weights = weight_root['fail']
        else:
            # 中奖时，需要层层深入获取对应的权重列表
            # 2. 投注模式模式
            weights = weight_root['success'][self.stake_mode]
            # 3.basic/free
            if self.round_mode == 1:
                weights = weights['basic']
            else:
                weights = weights['free']
                # 4. 免费模式下、根据已赢轮数选择对应的权重
                max_round_key = max(weights.keys())
                if self.succeed_rounds_free >= max_round_key:
                    weights = weights[max_round_key]
                else:
                    weights = weights[self.succeed_rounds_free + 1]

        # 5. 校验权重数组长度
        if len(weights) != len(odds_range):
            raise ValueError(f"Multi weights length ({len(weights)}) does not match odd_range length ({len(odds_range)}).")
        # 6. 根据权重抽取N个倍率值
        picked_odds = self.rng.choices(odds_range, weights=weights, k=self.multi_count)
        # 7. 将抽中的倍率值与其对应的图案ID（颜色）配对
        value_to_color_map = dict(zip(odds_range, color_keys))
        # 8. 构建 multi_picked_list，包含每个倍率及其对应的图案ID
        self.multi_picked_list = [[odd, value_to_color_map.get(odd)] for odd in picked_odds]
        # 记录multi图案的合计倍率值
        self.pattern_multiplier = sum(picked_odds)

    # 处理scatter图案
    def process_scatter_pattern(self):
        self.scatter_count = 0
        for col in range(6):
            for row in range(5):
                if self.matrix[col][row] == 10:  # scatter图案ID
                    self.scatter_count += 1
                
        # 根据scatter数量、round_mode，计算赔率&奖励局数
        self.scatter_odds = 0
        self.bonus_rounds_awarded = 0

        scatter_config = self.cfg['symbols_odds'][10]
        # 倒序查找，以匹配最高的奖励档位
        for i in range(len(scatter_config['quantity']) - 1, -1, -1):
            if self.scatter_count >= scatter_config['quantity'][i]:
                self.scatter_odds = scatter_config["odds"][i]
                break # 找到最高档位后即可停止

        # 1. 先判断游戏模式、再根据数量判断是否中奖
        if self.round_mode == 1:  # 普通模式
            # 2. 普通模式下4个以上scatter就算中奖
            if self.scatter_count >= 4:
                # 3. 奖励次数：普通模式15次
                self.bonus_rounds_awarded = scatter_config["free_rounds_awards"][0]
        else:  # 免费模式 (round_mode == 2)
            # 2. 免费模式下3个以上scatter就算中奖
            if self.scatter_count >= 3:
                # 3. 奖励次数：免费模式5次
                self.bonus_rounds_awarded = scatter_config["free_rounds_awards"][1]

    # 得分与rounds结算
    def setting_round(self):
        total_multiplier = self.pattern_multiplier + self.global_multiplier
        self.basic_odds = self.regular_odds * (total_multiplier if self.pattern_multiplier > 0 else 1)
        self.multi_odds = self.basic_odds - self.regular_odds
        self.scatter_odds = self.scatter_odds
        self.total_odds = self.basic_odds + self.scatter_odds
        self.bonus_rounds_awarded = self.bonus_rounds_awarded
        self.roll_number += 1
