from collections import defaultdict

class StateRolling:
    def __init__(self, reel_set_id, matrix, rng, cfg):
        self.reel_set_id = reel_set_id    # 本轮游戏的控制数据
        self.matrix = matrix    # 当前图案矩阵、列为第一维
        self.rng = rng
        self.cfg = cfg

    # 生成新的图案矩阵：根据现有图案矩阵&选中的实体轴编号、生成新的健全（没有空图案）的图案矩阵
    def patch_matrix(self):
        # 深复制（列为第一维）
        matrix_tem = [col[:] for col in self.matrix]

        # 获取该 reel_set 的 6 条列条带
        reel_set = self.cfg['reel_sets'][self.reel_set_id]

        for col in range(6):
            # 统计该列空位（按从上到下顺序）。假设空位都是顶部连续区域；若不是也逐个填充。
            empty_positions = [row for row in range(5) if matrix_tem[col][row] == 0]
            empty_count = len(empty_positions)
            if empty_count == 0:
                continue

            # 具体的某一条轴的实轴列表（第1元素是标号、第2元素是列表）
            reel_strip = reel_set[col][1]
            strip_len = len(reel_strip)
            if strip_len == 0:
                continue

            # 随机选择一个起点，取连续 empty_count 个元素（循环）
            start_idx = self.rng.randint(0, strip_len - 1)
            window_symbols = [reel_strip[(start_idx + offset) % strip_len] for offset in range(empty_count)]

            # 按空位出现顺序填充（通常是从顶部往下）
            for pos, symbol in zip(empty_positions, window_symbols):
                matrix_tem[col][pos] = symbol

        self.matrix = matrix_tem

    # 处理图案中奖消除的过程（仅普通图案会消除key1~9)、并计算其得分
    def process_regular_pattern(self):  
        # 统计每种图案的数量和位置
        symbol_counts = defaultdict(int)  # 自动初始化为0
        symbol_positions = defaultdict(list)  # 自动初始化为空列表

        # 遍历矩阵统计图案
        for col in range(6):
            for row in range(5):
                symbol = self.matrix[col][row]
                if symbol == 0:
                    continue

                # 处理普通图案(1-9)
                if 1 <= symbol <= 9:
                    symbol_counts[symbol] += 1
                    symbol_positions[symbol].append((col, row))

        # 检查普通图案中奖并计算总倍率
        self.regular_odds = 0
        winning_positions = set()  # 存储所有中奖的普通图案位置
        self.winning_symbols_details = {}  # 存储每种图案的中奖详情

        for symbol_id, count in symbol_counts.items():
            if symbol_id not in self.cfg['symbols_odds']:
                continue

            symbol_config = self.cfg['symbols_odds'][symbol_id]
            quantity_requirements = symbol_config["quantity"]
            odds = symbol_config["odds"]
            
            # 从最高要求开始检查（倒序遍历）
            for i in range(len(quantity_requirements) - 1, -1, -1):
                if count >= quantity_requirements[i]:
                    symbol_odds = odds[i]
                    self.regular_odds += symbol_odds
                    winning_positions.update(symbol_positions[symbol_id])
                    
                    # 保存每种图案的中奖详情
                    self.winning_symbols_details[symbol_id] = {
                        'count': count,
                        'required_count': quantity_requirements[i],
                        'odds': symbol_odds,
                        'positions': symbol_positions[symbol_id][:]
                    }
                    break

        # 如果没有中奖，直接设置结果并返回，避免不必要的矩阵操作
        if not winning_positions:
            self.regular_odds = 0
            self.winning_symbols_details = {}
            return

        # 创建新矩阵，移除中奖的普通图案
        matrix_tem = [[0 for _ in range(5)] for _ in range(6)]

        # 复制所有非中奖的图案
        for col in range(6):
            for row in range(5):
                symbol = self.matrix[col][row]
                # 保留非中奖的图案
                if (col, row) not in winning_positions:
                    matrix_tem[col][row] = symbol

        # 实现图案下坠效果（重力效果）
        for col in range(6):
            # 1. 从当前列收集所有非零的图案（保持原有顺序）
            non_zero_symbols = [matrix_tem[col][row] for row in range(5) if matrix_tem[col][row] != 0]
            # 2. 计算需要填充的空位数
            num_zeros = 5 - len(non_zero_symbols)
            # 3. 构建新列：顶部是空位，底部是图案
            new_col_data = [0] * num_zeros + non_zero_symbols
            # 4. 将新列数据写回矩阵
            for row in range(5):
                matrix_tem[col][row] = new_col_data[row]

        self.matrix = matrix_tem
