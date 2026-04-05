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
        "awards": {
            "base_trigger": {"free_spins": 15},
            "feature_retrigger": {"free_spins": 5},
        },
    },
    11 :{
        "symbol_name": "multiplier",
        "symbol_type": "multiplier",    # multiplier symbol with different color consider to be the same symbol in the backend
    },
}

# 倍率图案携带数值与其数值权重组
# 倍率数值是离散的、2~500共15个、权重组数量不定（最少1个）
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
# 字典编号用于区分不同的条带组、数量与后文Control字段xxxx相对应
# 数组编号用于区分条带组组内编号、固定为6个[1~6]、对应游戏机台滚轴一共6列
# 组内数值编号区分不同的实体图案、范围固定[1~11]、对应PAYTABLE字段下的1~11个字段、即对应蓝宝石图案 ~ 倍率图案
# 条带内的图案具有上下的物理位置关系、而条带间的图案没有左右的物理位置关系；即：
#   出现在同一条带的相邻上\下方位的其他图案、落在机台上时也具有相邻的上\下位置关系；
#   条带落在机台上哪一条滚轴并不唯一确定、而是每次生成图案时抽取
# 具体生成图案时:
#   先确定使用的条带组（字典）
#   再确定当前轴体使用的条带（数组）
#       再从数组随机位置取出连续的若干个图案（数值1~11）
#           当从条带中取出连续的若干个图案时，如果超过条带末尾，则从条带开头继续取，形成循环抽取
#   再从剩下的条带组中抽取未使用过的条带（数组）、重复6次直到全部条带使用完毕
# Virtual Reel Strips
# Dictionary Index: Used to distinguish between different sets of reel strips; the quantity corresponds to the `xxxx` value in the subsequent `Control` field.
# Array Index: Used to distinguish individual strips within a specific set; fixed at 6 indices [1–6], corresponding to the 6 columns (reels) on the gaming machine.
# Value Index: Used to distinguish between different physical symbols; fixed range [1–11], corresponding to the 1–11 entries listed under the `PAYTABLE` field—specifically, ranging from the Sapphire symbol to the Multiplier symbol.
# Symbols *within* a single strip possess a fixed vertical (up/down) physical positional relationship relative to one another; however, symbols *across* different strips possess no fixed horizontal (left/right) physical positional relationship. Specifically:
#   Any symbols appearing in adjacent vertical positions (above or below one another) within the same strip will retain this adjacent vertical relationship when they land on the gaming machine's reels.
#   The specific reel (column) onto which a given strip lands is not predetermined; instead, it is assigned randomly per roll (not fixed across wagers) symbols are generated.
# The specific process for generating symbols is as follows:
#   First, determine which set of reel strips (Dictionary) will be used.
#   Next, determine which specific strip (Array) will be used for the current reel.
#       Then, select a consecutive sequence of symbols (Values ​​1–11) starting from a random position within that strip.
#           When selecting a consecutive sequence of symbols from a strip, if the selection extends beyond the end of the strip, the sequence wraps around and continues from the beginning of the strip (creating a cyclical selection).
#   Finally, select an unused strip (Array) from the remaining set of strips; repeat this process 6 times until all strips have been utilized.
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