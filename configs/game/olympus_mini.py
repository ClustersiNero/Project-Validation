# Wager mode configuration
WAGER_MODE = {
    1 :{
        "mode_name": "normal",
        "wager_cost_multiplier": 1.0,
    },
    2 :{
        "mode_name": "feature_buy",
        "wager_cost_multiplier": 80.0,
    },
    3 :{
        "mode_name": "chance_increase",
        "wager_cost_multiplier": 1.25,
    },
}

# Paytable
PAYTABLE = {
    1 :{
        "symbol_name": "blue_gem",
        "symbol_type": "regular",
        "payouts": {
            8: 0.25,
            10: 0.75,
            12: 2.0,
        },
    },
    2 :{
        "symbol_name": "green_gem",
        "symbol_type": "regular",
        "payouts": {
            8: 0.4,
            10: 0.9,
            12: 4.0,
        },
    },
    3 :{
        "symbol_name": "yellow_gem",
        "symbol_type": "regular",
        "payouts": {
            8: 0.5,
            10: 1.0,
            12: 5.0,
        },
    },
    4 :{
        "symbol_name": "purple_gem",
        "symbol_type": "regular",
        "payouts": {
            8: 0.8,
            10: 1.2,
            12: 8.0,
        },
    },
    5 :{
        "symbol_name": "red_gem",
        "symbol_type": "regular",
        "payouts": {
            8: 1.0,
            10: 1.5,
            12: 10.0,
        },
    },
    6 :{
        "symbol_name": "wineglass",
        "symbol_type": "regular",
        "payouts": {
            8: 1.5,
            10: 2.0,
            12: 12.0,
        },
    },
    7 :{
        "symbol_name": "ring",
        "symbol_type": "regular",
        "payouts": {
            8: 2.0,
            10: 5.0,
            12: 15.0,
        },
    },
    8 :{
        "symbol_name": "hourglass",
        "symbol_type": "regular",
        "payouts": {
            8: 2.5,
            10: 10.0,
            12: 25.0,
        },
    },
    9 :{
        "symbol_name": "crown",
        "symbol_type": "regular",
        "payouts": {
            8: 10.0,
            10: 25.0,
            12: 50.0,
        },
    },
    10 :{
        "symbol_name": "zeus",
        "symbol_type": "scatter",
        "payouts": {
            4: 3.0,
            5: 5.0,
            6: 100.0,
        },
    },
    11 :{
        "symbol_name": "multiplier",
        "symbol_type": "multiplier",    # multiplier symbol with different color consider to be the same symbol in the backend
    },
}

# 倍率图案携带数值与其数值权重组
# 倍率数值是离散的、2~500共15个、权重组数量不定（最少1个）
# Multiplier Pattern: Associated Values ​​and Weight Groups
# The multiplier values ​​are discrete, comprising 15 distinct values ​​ranging from 2 to 500; the number of weight groups is variable (with a minimum of one).
MULTIPLIER_DATA = {
    'value': [2,    3,   4,   5,   6,   8,  10, 12, 15, 20, 25, 50, 100, 250, 500],
    'weight': {
          1: [1087, 610, 377, 233, 144, 89, 55, 34, 21, 13, 8,  5,  3,   2,   1],
          2: [1087, 610, 377, 233, 144, 89, 55, 34, 21, 13, 8,  5,  0,   0,   0],
          3: [1087, 610, 377, 233, 144, 89, 55, 0,  0,  0,  0,  0,  0,   0,   0],
          4: [1087, 610, 377, 0,   0,   0,  0,  0,  0,  0,  0,  0,  0,   0,   0],
    }
}

# 虚拟实体条带
# 字典编号用于区分不同的条带组、数量与后文实现配置字段相对应
# 数组编号用于区分条带组内的不同条带、固定为6个[1~6]、对应机台一共6列
# 组内数值范围固定[1~11]、对应PAYTABLE中的图案id
#
# 条带内图案具有上下物理位置关系；
# 不同条带之间没有固定的左右物理位置关系。
#
# 具体生成流程：
#   1. 先确定本round使用的条带组（strip set）
#   2. 在该条带组内，将6条条带编号做一次随机打乱
#   3. 打乱后的结果按列依次分配到6列，因此：
#        - 同一round内，每列使用的条带互不重复
#        - 同一round内，列与条带的对应关系在round开始时一次性确定
#   4. 每列再从各自条带中的随机起点，循环截取连续若干个图案，组成初始board
#   5. 若本round内发生消除补位，则继续复用当前round已经确定的条带组与列条带对应关系；
#      refill不会重新选择条带组，也不会重新打乱列条带顺序
#
# 也就是说：
#   - 不同round之间，列与条带的对应顺序可以不同
#   - 同一round内，初始落板与后续refill使用的是同一套列条带映射

# Virtual Reel Strips
# The outer dictionary key identifies a strip set.
# The inner keys [1~6] identify the 6 strips inside that strip set, corresponding to the 6 board columns.
# Symbol ids inside each strip map directly to PAYTABLE symbol ids.
#
# Symbols within a single strip preserve vertical adjacency.
# Different strips do not have any fixed horizontal relationship before assignment to columns.
#
# Generation flow:
#   1. First select the strip set for the current round.
#   2. Then shuffle the 6 strip ids inside that strip set once.
#   3. The shuffled order is assigned to the 6 columns in order, which means:
#        - within the same round, each column uses a distinct strip
#        - the column-to-strip mapping is fixed once at round start
#   4. For each column, a random start position is chosen on its assigned strip,
#      and a cyclic slice is taken to form the initial board
#   5. If cascades/refills happen within the same round, the engine reuses the same
#      round-selected strip set and the same column-to-strip mapping;
#      refill does not reselect the strip set and does not reshuffle strip order
#
# In other words:
#   - across different rounds, the column-to-strip order may differ
#   - within the same round, the initial board and all refills use the same column-strip mapping

STRIP_SETS  = {
    1 : {
        1: [6, 2, 3, 7, 5, 7, 4, 4, 4, 7, 1, 4, 7, 2, 5, 2, 2, 2, 8, 8, 1, 1, 6, 8, 1, 5, 1, 2, 4, 4, 7, 4, 4, 6, 3, 3, 5, 2, 3, 4, 5, 5, 1, 4, 4, 5, 1, 2, 2, 2, 1, 8, 8, 7, 1, 8, 9, 9, 4, 5, 4, 8, 5, 5, 2, 2, 2, 2, 6, 6, 3, 7, 7, 7, 2, 1, 9, 9, 1, 4, 6, 7, 9, 9, 3, 3, 2, 2, 2, 2, 3, 2, 5, 1, 8, 6, 6, 6, 8, 1, 7, 3, 1, 1, 3, 5, 5, 7, 1, 8, 8, 1, 1, 2, 6, 8, 3, 3, 3, 2, 8, 7, 7, 5, 6, 5, 5, 4, 1, 1, 5, 5, 5, 1, 1, 1, 3, 2, 4, 4, 5, 1, 2, 9, 9, 7, 5, 3, 3, 1, 1, 7, 4, 6, 5, 9, 9, 8, 8, 8, 3, 4, 3, 3, 3, 4, 6, 5, 4, 2, 3, 7, 4, 4, 8, 8, 7, 3, 6, 6, 3, 6, 3, 6, 6, 3, 6, 7, 7, 1, 2, 4, 1, 1, 9, 9, 6, 9, 3, 6],
        2: [5, 9, 9, 3, 5, 7, 1, 1, 1, 5, 1, 9, 9, 8, 8, 9, 9, 1, 6, 6, 6, 6, 8, 8, 1, 1, 1, 1, 6, 7, 7, 7, 6, 6, 8, 7, 4, 1, 8, 2, 1, 8, 8, 2, 8, 6, 8, 8, 2, 3, 4, 5, 5, 2, 2, 2, 7, 5, 5, 4, 2, 4, 6, 6, 6, 6, 3, 4, 2, 1, 1, 8, 4, 3, 3, 1, 7, 2, 3, 2, 6, 5, 2, 4, 4, 4, 2, 4, 4, 3, 5, 8, 7, 7, 2, 6, 2, 2, 6, 3, 9, 9, 3, 5, 1, 7, 7, 1, 1, 1, 3, 3, 1, 4, 3, 8, 8, 4, 4, 7, 6, 4, 1, 3, 3, 3, 7, 7, 9, 4, 1, 8, 7, 1, 7, 9, 2, 3, 8, 2, 2, 1, 1, 1, 7, 8, 4, 2, 2, 4, 6, 3, 4, 5, 7, 4, 3, 9, 2, 2, 2, 6, 4, 4, 5, 3, 2, 2, 5, 5, 9, 5, 5, 4, 3, 3, 7, 3, 3, 9, 3, 1, 1, 6, 5, 5, 1, 1, 5, 3, 3, 6, 2, 1, 4, 5, 2, 9, 5, 5],
        3: [4, 1, 1, 1, 6, 4, 3, 6, 3, 2, 1, 1, 2, 9, 7, 2, 5, 6, 5, 3, 6, 2, 6, 6, 8, 2, 5, 9, 4, 4, 6, 1, 1, 1, 6, 1, 6, 2, 5, 2, 1, 5, 4, 5, 4, 4, 4, 2, 3, 3, 3, 3, 1, 2, 4, 3, 3, 3, 8, 4, 6, 4, 7, 7, 2, 5, 5, 1, 3, 9, 8, 8, 8, 5, 1, 1, 3, 3, 5, 5, 8, 5, 3, 9, 6, 3, 6, 5, 4, 3, 3, 3, 9, 9, 9, 9, 7, 7, 2, 2, 7, 7, 7, 8, 8, 1, 4, 6, 6, 6, 6, 2, 7, 5, 1, 6, 3, 7, 7, 7, 9, 4, 2, 8, 8, 4, 4, 3, 3, 2, 2, 7, 8, 8, 7, 4, 5, 4, 4, 6, 6, 8, 8, 8, 4, 2, 6, 1, 7, 7, 2, 2, 4, 7, 1, 1, 1, 2, 2, 2, 7, 7, 5, 5, 4, 9, 9, 1, 2, 3, 9, 2, 1, 9, 2, 5, 2, 2, 1, 6, 8, 8, 5, 9, 1, 1, 4, 1, 1, 5, 5, 6, 1, 3, 2, 4, 3, 3, 2, 8],
        4: [3, 4, 4, 4, 1, 1, 1, 5, 4, 8, 6, 6, 6, 4, 4, 2, 2, 5, 8, 4, 7, 1, 5, 6, 6, 7, 1, 1, 3, 1, 4, 4, 3, 3, 4, 3, 3, 2, 8, 4, 2, 1, 9, 6, 2, 2, 8, 9, 3, 2, 2, 1, 1, 6, 7, 1, 5, 1, 1, 1, 2, 7, 8, 8, 7, 9, 1, 1, 3, 3, 3, 3, 2, 8, 9, 9, 6, 6, 3, 3, 3, 3, 1, 4, 4, 1, 6, 6, 5, 5, 4, 9, 9, 7, 3, 9, 7, 7, 3, 7, 8, 9, 9, 7, 5, 1, 1, 8, 8, 8, 3, 7, 7, 1, 1, 1, 4, 9, 9, 5, 1, 1, 1, 7, 8, 5, 3, 5, 2, 6, 4, 4, 4, 4, 1, 5, 6, 7, 8, 5, 8, 1, 1, 4, 4, 6, 6, 6, 2, 2, 5, 2, 2, 3, 8, 5, 2, 5, 3, 3, 3, 3, 8, 2, 7, 7, 4, 2, 5, 5, 6, 2, 4, 2, 2, 4, 2, 2, 5, 6, 9, 7, 2, 6, 2, 7, 2, 2, 6, 8, 5, 2, 9, 5, 3, 5, 3, 8, 5, 7],
        5: [2, 6, 1, 9, 8, 1, 2, 6, 9, 5, 9, 9, 1, 9, 4, 4, 1, 1, 4, 5, 7, 7, 3, 2, 2, 2, 9, 9, 9, 7, 4, 7, 6, 6, 6, 2, 2, 8, 8, 8, 8, 2, 2, 2, 3, 3, 7, 2, 2, 4, 6, 3, 2, 2, 5, 2, 1, 3, 2, 5, 1, 7, 1, 8, 8, 8, 4, 4, 4, 5, 1, 1, 1, 5, 9, 3, 6, 6, 7, 1, 2, 6, 6, 2, 1, 5, 3, 5, 8, 3, 4, 4, 3, 1, 4, 4, 4, 6, 6, 6, 4, 8, 8, 9, 8, 8, 5, 5, 5, 5, 2, 4, 2, 6, 4, 3, 9, 6, 1, 3, 3, 5, 5, 6, 3, 3, 1, 7, 7, 1, 1, 7, 7, 7, 6, 1, 3, 5, 3, 4, 4, 4, 6, 4, 4, 2, 3, 3, 6, 7, 3, 2, 2, 1, 1, 1, 6, 4, 4, 1, 1, 6, 7, 3, 7, 7, 7, 8, 5, 8, 7, 8, 9, 1, 5, 8, 3, 3, 1, 1, 2, 2, 3, 3, 9, 5, 1, 4, 5, 5, 6, 7, 4, 2, 9, 5, 1, 3, 2, 8],
        6: [1, 1, 2, 1, 2, 1, 1, 3, 8, 4, 5, 8, 8, 2, 6, 6, 6, 1, 1, 6, 6, 6, 6, 7, 7, 1, 1, 8, 7, 6, 1, 6, 3, 5, 9, 1, 2, 4, 3, 9, 9, 6, 2, 2, 2, 6, 1, 1, 7, 7, 3, 3, 4, 4, 5, 5, 5, 7, 2, 2, 4, 2, 7, 7, 7, 1, 5, 3, 9, 3, 3, 2, 2, 8, 7, 1, 1, 2, 3, 3, 2, 9, 9, 4, 9, 3, 7, 7, 3, 3, 4, 4, 8, 3, 8, 8, 6, 6, 7, 1, 1, 6, 6, 2, 3, 8, 9, 9, 8, 8, 2, 9, 4, 4, 4, 2, 7, 5, 2, 7, 7, 4, 4, 3, 2, 2, 5, 6, 1, 3, 7, 1, 5, 8, 8, 8, 1, 2, 4, 7, 6, 8, 2, 3, 2, 4, 5, 5, 4, 4, 5, 6, 7, 4, 6, 1, 7, 4, 5, 3, 3, 3, 5, 5, 5, 1, 8, 8, 5, 1, 2, 2, 3, 2, 3, 9, 9, 3, 3, 3, 1, 1, 9, 1, 2, 5, 5, 1, 5, 4, 4, 4, 5, 6, 3, 4, 6, 4, 9, 1],
    },
    2 : {
        1: [10, 6, 2, 3, 7, 10, 5, 7, 4, 4, 10, 4, 7, 1, 4, 10, 7, 2, 5, 2, 10, 2, 2, 8, 8, 10, 1, 1, 6, 8, 11, 1, 5, 1, 2, 11, 4, 4, 7, 4, 4, 6, 3, 3, 5, 2, 3, 4, 5, 5, 1, 4, 4, 5, 1, 2, 2, 2, 1, 8, 8, 7, 1, 8, 9, 9, 4, 5, 4, 8, 5, 5, 2, 2, 2, 2, 6, 6, 3, 7, 7, 7, 2, 1, 9, 9, 1, 4, 6, 7, 9, 9, 3, 3, 2, 2, 2, 2, 3, 2, 5, 1, 8, 6, 6, 6, 8, 1, 7, 3, 1, 1, 3, 5, 5, 7, 1, 8, 8, 1, 1, 2, 6, 8, 3, 3, 3, 2, 8, 7, 7, 5, 6, 5, 5, 4, 1, 1, 5, 5, 5, 1, 1, 1, 3, 2, 4, 4, 5, 1, 2, 9, 9, 7, 5, 3, 3, 1, 1, 7, 4, 6, 5, 9, 9, 8, 8, 8, 3, 4, 3, 3, 3, 4, 6, 5, 4, 2, 3, 7, 4, 4, 8, 8, 7, 3, 6, 6, 3, 6, 3, 6, 6, 3, 6, 7, 7, 1, 2, 4, 1, 1, 9, 9, 6, 9, 3, 6],
        2: [10, 5, 9, 9, 3, 10, 5, 7, 1, 1, 10, 1, 5, 1, 9, 10, 9, 8, 8, 9, 10, 9, 1, 6, 6, 10, 6, 6, 8, 8, 11, 1, 1, 1, 1, 11, 6, 7, 7, 7, 6, 6, 8, 7, 4, 1, 8, 2, 1, 8, 8, 2, 8, 6, 8, 8, 2, 3, 4, 5, 5, 2, 2, 2, 7, 5, 5, 4, 2, 4, 6, 6, 6, 6, 3, 4, 2, 1, 1, 8, 4, 3, 3, 1, 7, 2, 3, 2, 6, 5, 2, 4, 4, 4, 2, 4, 4, 3, 5, 8, 7, 7, 2, 6, 2, 2, 6, 3, 9, 9, 3, 5, 1, 7, 7, 1, 1, 1, 3, 3, 1, 4, 3, 8, 8, 4, 4, 7, 6, 4, 1, 3, 3, 3, 7, 7, 9, 4, 1, 8, 7, 1, 7, 9, 2, 3, 8, 2, 2, 1, 1, 1, 7, 8, 4, 2, 2, 4, 6, 3, 4, 5, 7, 4, 3, 9, 2, 2, 2, 6, 4, 4, 5, 3, 2, 2, 5, 5, 9, 5, 5, 4, 3, 3, 7, 3, 3, 9, 3, 1, 1, 6, 5, 5, 1, 1, 5, 3, 3, 6, 2, 1, 4, 5, 2, 9, 5, 5],
        3: [10, 4, 1, 1, 1, 10, 6, 4, 3, 6, 10, 3, 2, 1, 1, 10, 2, 9, 7, 2, 10, 5, 6, 5, 3, 10, 6, 2, 6, 6, 11, 8, 2, 5, 9, 11, 4, 4, 6, 1, 1, 1, 6, 1, 6, 2, 5, 2, 1, 5, 4, 5, 4, 4, 4, 2, 3, 3, 3, 3, 1, 2, 4, 3, 3, 3, 8, 4, 6, 4, 7, 7, 2, 5, 5, 1, 3, 9, 8, 8, 8, 5, 1, 1, 3, 3, 5, 5, 8, 5, 3, 9, 6, 3, 6, 5, 4, 3, 3, 3, 9, 9, 9, 9, 7, 7, 2, 2, 7, 7, 7, 8, 8, 1, 4, 6, 6, 6, 6, 2, 7, 5, 1, 6, 3, 7, 7, 7, 9, 4, 2, 8, 8, 4, 4, 3, 3, 2, 2, 7, 8, 8, 7, 4, 5, 4, 4, 6, 6, 8, 8, 8, 4, 2, 6, 1, 7, 7, 2, 2, 4, 7, 1, 1, 1, 2, 2, 2, 7, 7, 5, 5, 4, 9, 9, 1, 2, 3, 9, 2, 1, 9, 2, 5, 2, 2, 1, 6, 8, 8, 5, 9, 1, 1, 4, 1, 1, 5, 5, 6, 1, 3, 2, 4, 3, 3, 2, 8],
        4: [10, 3, 4, 4, 4, 10, 1, 1, 1, 5, 10, 4, 8, 6, 6, 10, 6, 4, 4, 2, 10, 2, 5, 8, 4, 10, 7, 1, 5, 6, 11, 6, 7, 1, 1, 11, 3, 1, 4, 4, 3, 3, 4, 3, 3, 2, 8, 4, 2, 1, 9, 6, 2, 2, 8, 9, 3, 2, 2, 1, 1, 6, 7, 1, 5, 1, 1, 1, 2, 7, 8, 8, 7, 9, 1, 1, 3, 3, 3, 3, 2, 8, 9, 9, 6, 6, 3, 3, 3, 3, 1, 4, 4, 1, 6, 6, 5, 5, 4, 9, 9, 7, 3, 9, 7, 7, 3, 7, 8, 9, 9, 7, 5, 1, 1, 8, 8, 8, 3, 7, 7, 1, 1, 1, 4, 9, 9, 5, 1, 1, 1, 7, 8, 5, 3, 5, 2, 6, 4, 4, 4, 4, 1, 5, 6, 7, 8, 5, 8, 1, 1, 4, 4, 6, 6, 6, 2, 2, 5, 2, 2, 3, 8, 5, 2, 5, 3, 3, 3, 3, 8, 2, 7, 7, 4, 2, 5, 5, 6, 2, 4, 2, 2, 4, 2, 2, 5, 6, 9, 7, 2, 6, 2, 7, 2, 2, 6, 8, 5, 2, 9, 5, 3, 5, 3, 8, 5, 7],
        5: [10, 2, 6, 1, 9, 10, 8, 1, 2, 6, 10, 9, 5, 9, 9, 10, 1, 9, 4, 4, 10, 1, 1, 4, 5, 10, 7, 7, 3, 2, 11, 2, 2, 9, 9, 11, 9, 7, 4, 7, 6, 6, 6, 2, 2, 8, 8, 8, 8, 2, 2, 2, 3, 3, 7, 2, 2, 4, 6, 3, 2, 2, 5, 2, 1, 3, 2, 5, 1, 7, 1, 8, 8, 8, 4, 4, 4, 5, 1, 1, 1, 5, 9, 3, 6, 6, 7, 1, 2, 6, 6, 2, 1, 5, 3, 5, 8, 3, 4, 4, 3, 1, 4, 4, 4, 6, 6, 6, 4, 8, 8, 9, 8, 8, 5, 5, 5, 5, 2, 4, 2, 6, 4, 3, 9, 6, 1, 3, 3, 5, 5, 6, 3, 3, 1, 7, 7, 1, 1, 7, 7, 7, 6, 1, 3, 5, 3, 4, 4, 4, 6, 4, 4, 2, 3, 3, 6, 7, 3, 2, 2, 1, 1, 1, 6, 4, 4, 1, 1, 6, 7, 3, 7, 7, 7, 8, 5, 8, 7, 8, 9, 1, 5, 8, 3, 3, 1, 1, 2, 2, 3, 3, 9, 5, 1, 4, 5, 5, 6, 7, 4, 2, 9, 5, 1, 3, 2, 8],
        6: [10, 1, 1, 2, 1, 10, 2, 1, 1, 3, 10, 8, 4, 5, 8, 10, 8, 2, 6, 6, 10, 6, 1, 1, 6, 10, 6, 6, 6, 7, 11, 7, 1, 1, 8, 11, 7, 6, 1, 6, 3, 5, 9, 1, 2, 4, 3, 9, 9, 6, 2, 2, 2, 6, 1, 1, 7, 7, 3, 3, 4, 4, 5, 5, 5, 7, 2, 2, 4, 2, 7, 7, 7, 1, 5, 3, 9, 3, 3, 2, 2, 8, 7, 1, 1, 2, 3, 3, 2, 9, 9, 4, 9, 3, 7, 7, 3, 3, 4, 4, 8, 3, 8, 8, 6, 6, 7, 1, 1, 6, 6, 2, 3, 8, 9, 9, 8, 8, 2, 9, 4, 4, 4, 2, 7, 5, 2, 7, 7, 4, 4, 3, 2, 2, 5, 6, 1, 3, 7, 1, 5, 8, 8, 8, 1, 2, 4, 7, 6, 8, 2, 3, 2, 4, 5, 5, 4, 4, 5, 6, 7, 4, 6, 1, 7, 4, 5, 3, 3, 3, 5, 5, 5, 1, 8, 8, 5, 1, 2, 2, 3, 2, 3, 9, 9, 3, 3, 3, 1, 1, 9, 1, 2, 5, 5, 1, 5, 4, 4, 4, 5, 6, 3, 4, 6, 4, 9, 1],
    },
    3 : {
        1: [4, 3, 3, 7, 9, 4, 1, 1, 7, 4, 8, 5, 1, 5, 5, 6, 8, 1, 2, 8, 9, 7, 9, 7, 2, 2, 6, 6, 6, 2, 2, 2, 1, 3, 9, 4, 2, 1, 1, 3, 3, 5, 6, 3, 7, 8, 4, 8, 4, 5],
        2: [10, 4, 5, 5, 8, 10, 5, 4, 6, 6, 10, 3, 4, 4, 3, 10, 5, 7, 9, 3, 10, 2, 2, 1, 1, 10, 1, 7, 7, 1, 10, 8, 5, 6, 8, 10, 8, 3, 7, 3, 10, 2, 3, 4, 1, 10, 6, 8, 9, 9, 10, 2, 7, 1, 4, 10, 1, 2, 2, 9],
        3: [10, 7, 3, 7, 6, 10, 1, 1, 8, 3, 10, 3, 7, 1, 2, 10, 2, 4, 1, 6, 10, 6, 5, 5, 8, 10, 8, 8, 4, 3, 10, 3, 9, 4, 9, 10, 6, 2, 9, 9, 10, 5, 2, 4, 1, 10, 4, 2, 6, 7, 10, 7, 2, 1, 4, 10, 5, 3, 5, 8],
        4: [10, 7, 7, 1, 4, 10, 8, 8, 3, 9, 10, 2, 5, 2, 2, 10, 1, 1, 9, 7, 10, 4, 2, 9, 3, 10, 8, 8, 8, 5, 10, 3, 6, 9, 1, 10, 1, 5, 3, 2, 10, 5, 3, 1, 1, 10, 2, 4, 4, 5, 10, 6, 6, 7, 6, 10, 3, 4, 7, 4],
        5: [10, 6, 7, 5, 3, 10, 6, 1, 4, 7, 10, 6, 8, 1, 7, 10, 2, 6, 9, 2, 10, 4, 4, 9, 2, 10, 1, 5, 7, 3, 10, 3, 1, 1, 8, 10, 8, 4, 4, 9, 10, 1, 2, 2, 2, 10, 5, 1, 9, 2, 10, 3, 3, 3, 8, 10, 8, 7, 6, 5],
        6: [4, 1, 6, 6, 4, 3, 3, 6, 4, 7, 2, 5, 1, 9, 7, 7, 3, 8, 2, 5, 5, 2, 8, 8, 1, 5, 8, 3, 1, 1, 6, 6, 9, 2, 4, 4, 2, 7, 3, 5, 1, 7, 9, 9, 8, 2, 3, 2, 1, 4],
    },
}

# 游戏数值生成流程
# 最外层字典编号1~3对应投注模式1~3（normal、feature_buy、chance_increase）
# 首层字段'basic'和'free'对应基础游戏模式和免费游戏模式
# 次层字段'round_strip_set_weights'和'round_multiplier_profile_weights'对应虚拟实体条带组的选择权重和倍率图案数值权重组的选择权重；
# 完整游戏流程举例：
#   游戏总是从basic模式开始
#       当玩家投注后、系统根据投注模式（1~3）读取本字段内的1层对应字段、找到其下的‘basic'字段、
#       从中找到'round_strip_set_weights'字段，并根据其数值随机出一个条带组编号（该结果在整个round内保持不变）
#           如：投注模式1、便在IMPLEMENTATION_CONFIG[1]['basic']['round_strip_set_weights']中根据[90,10,0]的权重随机出一个条带组编号，如随机结果为1，则选择第1个条带组
#       系统生成图案后、若有倍率图案，则根据相同路径下的'round_multiplier_profile_weights'字段中的权重随机出一个权重组（该结果在整个round内保持不变）
#           如：继续上例、在IMPLEMENTATION_CONFIG[1]['basic']['round_multiplier_profile_weights']中的权重随机出一个权重组，如随机结果为3，则选择第3个权重组
#       再根据所选权重组随机出一个倍率数值
#           如：继续上例、从MULTIPLIER_DATA['weight'][3]中按权重随机选择一个倍率数值、如随机结果为5，则选择第五个倍率数值(6x)
#       若游戏中奖、消除、还需要继续生成图案，则继续使用当前round已选定的条带组与倍率权重组进行后续图案生成，直到本轮round结束
#   随后、若游戏结束，则进行结算，若命中free game触发条件，则进入免费游戏模式并以相同的流程进行游戏


# Game Value Generation Process
# The outermost dictionary keys (1–3) correspond to betting modes 1–3 (normal, feature_buy, chance_increase).
# The first-level keys, 'basic' and 'free', correspond to the base game mode and the free game mode, respectively.
# The second-level keys—'round_strip_set_weights' and 'round_multiplier_profile_weights'—correspond to the selection weights for the virtual reel strip groups and the selection weights for the multiplier symbol value weight groups, respectively.
# Example of the Complete Game Flow:
#   The game always begins in 'basic' mode.
#       Once the player places a bet, the system—based on the selected betting mode (1–3)—accesses the corresponding first-level key within the data structure. It then locates the 'basic' key underneath it,
#       finds the 'round_strip_set_weights' key within that section, and uses the associated values to randomly select a reel strip group ID (this selection remains fixed for the entire round).
#           E.g.: For Betting Mode 1, the system uses the weights [90, 10, 0] found in `IMPLEMENTATION_CONFIG[1]['basic']['round_strip_set_weights']` to randomly select a strip group ID. If the random result is 1, the 1st strip group is selected.
#       After the system generates the symbols, if any multiplier symbols are present, it uses the weights found in the 'round_multiplier_profile_weights' key (located at the same path) to randomly select a multiplier weight group (this selection remains fixed for the entire round).
#           E.g.: Continuing the previous example, the system uses the weights in `IMPLEMENTATION_CONFIG[1]['basic']['round_multiplier_profile_weights']` to randomly select a weight group. If the random result is 3, the 3rd weight group is selected.
#       Subsequently, the system uses the selected weight group to randomly select a specific multiplier value.
#           E.g.: Continuing the previous example, the system randomly selects a multiplier value from `MULTIPLIER_DATA['weight'][3]` based on the defined weights. If the random result is 5, the fifth multiplier value (6x) is selected.
#       If the game results in a win, triggers a symbol elimination, and requires further symbol generation,
#       the system continues using the same reel strip group and multiplier profile selected at the start of the current round, until the round concludes.
#   Subsequently, if the game session ends, the system proceeds to settle the winnings. If the trigger conditions for the Free Game mode are met, the game transitions into Free Game mode and continues according to the exact same process.

IMPLEMENTATION_CONFIG = {
    1:{
        'basic':{
            'round_strip_set_weights': [90, 10, 0],             # index 0/1/2 → strip_set_id 1/2/3
            'round_multiplier_profile_weights': [1, 1, 2, 3],   # index 0/1/2/3 → multiplier_profile_id 1/2/3/4
        },
        'free':{
            'round_strip_set_weights': [50, 50, 0],
            'round_multiplier_profile_weights': [1, 1, 1, 1],
        },
    },
    2:{
        'basic':{
            'round_strip_set_weights': [0, 0, 1],
            'round_multiplier_profile_weights': [1, 1, 2, 3],
        },
        'free':{
            'round_strip_set_weights': [50, 50, 0],
            'round_multiplier_profile_weights': [1, 1, 1, 1],
        },
    },
    3:{
        'basic':{
            'round_strip_set_weights': [80, 20, 0],
            'round_multiplier_profile_weights': [1, 1, 2, 3],
        },
        'free':{
            'round_strip_set_weights': [50, 50, 0],
            'round_multiplier_profile_weights': [1, 1, 1, 1],
        },
    },
}