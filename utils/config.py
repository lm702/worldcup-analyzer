DIMENSION_WEIGHTS: dict[str, float] = {
    "position_distribution": 0.10,
    "fatigue_management": 0.15,
    "knockout_adaptability": 0.30,
    "venue_adaptation": 0.10,
    "substitution_strategy": 0.20,
    "yellow_card_risk": 0.15,
}

DEFAULT_N_SIMULATIONS = 10000

OVERALL_RATING_WEIGHT = 0.7
ELO_WEIGHT = 0.3

POSITION_TARGETS: dict[str, int] = {
    "GK": 3,
    "DEF": 9,
    "MID": 6,
    "FWD": 5,
}

IDEA_AGE_RANGE = (24, 29)

HIGH_DISCIPLINE_THRESHOLD = 0.3
