ALL_GROUPS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]

POSITION_LABELS: dict[str, str] = {
    "GK": "门将",
    "CB": "中卫",
    "LB": "左后卫",
    "RB": "右后卫",
    "WB": "边翼卫",
    "DM": "防守中场",
    "CM": "中场",
    "AM": "进攻中场",
    "LW": "左边锋",
    "RW": "右边锋",
    "ST": "中锋",
    "CF": "二前锋",
}

CATEGORY_LABELS: dict[str, str] = {
    "GK": "门将",
    "DEF": "后卫",
    "MID": "中场",
    "FWD": "前锋",
}

DIMENSION_LABELS: dict[str, str] = {
    "position_distribution": "位置分布",
    "fatigue_management": "疲劳管理",
    "knockout_adaptability": "淘汰赛适应性",
    "venue_adaptation": "场地适应",
    "substitution_strategy": "换人策略",
    "yellow_card_risk": "黄牌风险",
}

MATCH_STAGES: dict[str, str] = {
    "group": "小组赛",
    "round32": "32进16",
    "round16": "16强",
    "quarter": "1/4决赛",
    "semi": "半决赛",
    "final": "决赛",
}

VENUE_CITIES = [
    "波士顿", "迈阿密", "纽约/新泽西", "费城", "亚特兰大",
    "达拉斯", "休斯顿", "堪萨斯城", "洛杉矶", "旧金山湾区",
    "西雅图", "温哥华", "多伦多", "墨西哥城", "瓜达拉哈拉", "蒙特雷",
]

DIMENSION_ORDER = [
    "position_distribution",
    "fatigue_management",
    "knockout_adaptability",
    "venue_adaptation",
    "substitution_strategy",
    "yellow_card_risk",
]
