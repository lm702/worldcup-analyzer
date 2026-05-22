"""
赔率交叉参考引擎 — 去水 → 模型概率 → EV → Kelly
"""
from typing import Optional
from core.models import (
    MatchOdds, MoneylineOdds, AsianHandicap, OverUnder,
    SixDimensionAnalysis, ValueBet,
)
from utils.config import OVERALL_RATING_WEIGHT, ELO_WEIGHT


def implied_prob(odds: float) -> float:
    """小数赔率 → 隐含概率"""
    return 1.0 / odds


def remove_vig(moneyline: MoneylineOdds) -> tuple[float, float, float]:
    """去水：假设均匀去水"""
    h = implied_prob(moneyline.home_win)
    d = implied_prob(moneyline.draw)
    a = implied_prob(moneyline.away_win)
    total = h + d + a
    return h / total, d / total, a / total


def moneyline_vig(moneyline: MoneylineOdds) -> float:
    """计算水钱比例"""
    total = implied_prob(moneyline.home_win) + implied_prob(moneyline.draw) + implied_prob(moneyline.away_win)
    return round((total - 1) * 100, 1)


def model_prob_from_ratings(
    home_analysis: SixDimensionAnalysis,
    away_analysis: SixDimensionAnalysis,
) -> tuple[float, float, float]:
    """基于6维评分 + 球星差距 估算胜平负概率"""
    import math
    h = home_analysis.overall_rating
    a = away_analysis.overall_rating

    h_stars = home_analysis.knockout_adaptability.evidence.get("star_count", 0)
    a_stars = away_analysis.knockout_adaptability.evidence.get("star_count", 0)
    star_gap = (h_stars - a_stars) * 1.5

    h_caps = home_analysis.knockout_adaptability.evidence.get("total_caps", 0)
    a_caps = away_analysis.knockout_adaptability.evidence.get("total_caps", 0)
    caps_gap = (h_caps - a_caps) / 100.0 * 0.8

    effective_gap = (h - a) + star_gap + caps_gap
    diff = effective_gap / 10.0

    raw_h = 1.0 / (1.0 + 10.0 ** (-diff))
    raw_a = 1.0 - raw_h

    draw_prob = 0.30 * math.exp(-abs(diff) * 0.8)
    draw_prob = max(0.14, min(0.33, draw_prob))

    home_w = raw_h * (1.0 - draw_prob)
    away_w = raw_a * (1.0 - draw_prob)
    total = home_w + away_w + draw_prob

    return round(home_w / total, 3), round(draw_prob / total, 3), round(away_w / total, 3)


def compute_value_bets(
    odds: MatchOdds,
    home_analysis: SixDimensionAnalysis,
    away_analysis: SixDimensionAnalysis,
    home_team: str = "主队",
    away_team: str = "客队",
) -> list[ValueBet]:
    """比较市场赔率和模型概率，产出价值注列表"""
    bets: list[ValueBet] = []

    if odds.moneyline:
        h_prob, d_prob, a_prob = model_prob_from_ratings(home_analysis, away_analysis)
        vig = moneyline_vig(odds.moneyline)

        markets = [
            (home_team, odds.moneyline.home_win, h_prob, "胜平负"),
            ("平局", odds.moneyline.draw, d_prob, "胜平负"),
            (away_team, odds.moneyline.away_win, a_prob, "胜平负"),
        ]
        for selection, od, model_p, mkt in markets:
            implied = implied_prob(od)
            ev = model_p * od - 1
            kelly = ev / (od - 1) if od > 1 else 0
            confidence = _confidence(ev)
            rec = _recommendation(ev)
            bets.append(ValueBet(
                market_type=mkt,
                selection=selection,
                odds=round(od, 2),
                implied_prob=round(implied, 3),
                model_prob=round(model_p, 3),
                expected_value=round(ev, 4),
                kelly_fraction=round(max(0, kelly), 4),
                confidence=confidence,
                recommendation=rec,
            ))

    if odds.asian_handicap:
        ah = odds.asian_handicap
        model_h = h_prob + d_prob * _ah_draw_factor(ah.line)
        model_a = 1.0 - model_h
        h_implied = implied_prob(ah.home_odds)
        a_implied = implied_prob(ah.away_odds)

        for selection, model_p, od, mkt in [
            (f"{home_team} {ah.line:+.1f}", model_h, ah.home_odds, "亚洲盘口"),
            (f"{away_team} {ah.line:-.1f}", model_a, ah.away_odds, "亚洲盘口"),
        ]:
            ev = model_p * od - 1
            kelly = ev / (od - 1) if od > 1 else 0
            bets.append(ValueBet(
                market_type=mkt,
                selection=selection,
                odds=round(od, 2),
                implied_prob=round(implied_prob(od), 3),
                model_prob=round(model_p, 3),
                expected_value=round(ev, 4),
                kelly_fraction=round(max(0, kelly), 4),
                confidence=_confidence(ev),
                recommendation=_recommendation(ev),
            ))

    if odds.over_under:
        ou = odds.over_under
        prob_over = _ou_prob(home_analysis.overall_rating, away_analysis.overall_rating, ou.line)
        prob_under = 1.0 - prob_over

        for selection, model_p, od in [
            (f"大{ou.line}", prob_over, ou.over_odds),
            (f"小{ou.line}", prob_under, ou.under_odds),
        ]:
            ev = model_p * od - 1
            kelly = ev / (od - 1) if od > 1 else 0
            bets.append(ValueBet(
                market_type="大小球",
                selection=selection,
                odds=round(od, 2),
                implied_prob=round(implied_prob(od), 3),
                model_prob=round(model_p, 3),
                expected_value=round(ev, 4),
                kelly_fraction=round(max(0, kelly), 4),
                confidence=_confidence(ev),
                recommendation=_recommendation(ev),
            ))

    bets.sort(key=lambda b: -b.expected_value)
    return bets


def _confidence(ev: float) -> str:
    if ev > 0.10:
        return "high"
    if ev > 0.03:
        return "medium"
    return "low"


def _recommendation(ev: float) -> str:
    if ev > 0.05:
        return "推荐"
    if ev > 0:
        return "观望"
    return "不推荐"


def _ah_draw_factor(line: float) -> float:
    abs_l = abs(line)
    if abs_l <= 0.25:
        return 0.50
    if abs_l <= 0.5:
        return 0.35
    if abs_l <= 0.75:
        return 0.25
    if abs_l <= 1.0:
        return 0.15
    return 0.05


def _ou_prob(home_rating: float, away_rating: float, line: float) -> float:
    import math
    expected_goals = (home_rating / 100.0) * 2.5 + (away_rating / 100.0) * 1.8
    expected_goals = max(1.5, min(5.0, expected_goals))

    prob_under = 0.0
    for k in range(int(line) + 1):
        prob_under += (expected_goals ** k) * math.exp(-expected_goals) / math.factorial(k)

    prob_over = 1.0 - prob_under
    return round(float(prob_over), 3)
