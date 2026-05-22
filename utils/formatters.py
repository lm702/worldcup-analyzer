from core.models import Position
from utils.constants import POSITION_LABELS, CATEGORY_LABELS, MATCH_STAGES


def fmt_odds(odds: float) -> str:
    return f"{odds:.2f}"


def fmt_prob(prob: float) -> str:
    return f"{prob * 100:.1f}%"


def fmt_ev(ev: float) -> str:
    sign = "+" if ev >= 0 else ""
    return f"{sign}{ev * 100:.1f}%"


def fmt_kelly(kelly: float) -> str:
    return f"{kelly * 100:.1f}%"


def pos_label(position: Position) -> str:
    return POSITION_LABELS.get(position.value, position.value)


def cat_label(category: str) -> str:
    return CATEGORY_LABELS.get(category, category)


def stage_label(stage: str) -> str:
    return MATCH_STAGES.get(stage, stage)


def age_label(age: int) -> str:
    if age >= 33:
        return f"⚡高龄 ({age}岁)"
    if age >= 29:
        return f"巅峰末 ({age}岁)"
    if age >= 24:
        return f"黄金期 ({age}岁)"
    if age >= 21:
        return f"成长期 ({age}岁)"
    return f"新星 ({age}岁)"


def confidence_label(conf: str) -> str:
    labels = {"high": "高", "medium": "中", "low": "低"}
    return labels.get(conf, conf)


def format_score_distribution(probs: dict[str, float], top_n: int = 5) -> list[tuple[str, float]]:
    sorted_scores = sorted(probs.items(), key=lambda x: -x[1])
    return sorted_scores[:top_n]
