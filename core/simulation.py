"""
蒙特卡洛比赛模拟器 — 基于6维评分 + Poisson分布
"""
import math
import random
from collections import Counter
from typing import Optional

from core.models import SixDimensionAnalysis, SimulationParams, SimulationResult


def _rating_to_xg_pair(
    home_analysis: SixDimensionAnalysis,
    away_analysis: SixDimensionAnalysis,
    home_adj: dict | None = None,
    away_adj: dict | None = None,
) -> tuple[float, float]:
    """从模型概率反推期望进球对

    先用 model_prob_from_ratings 算胜平负概率，
    再通过 Win/Draw/Loss 约束反推期望进球值。
    """
    from core.value_bet import model_prob_from_ratings
    hp, dp, ap = model_prob_from_ratings(home_analysis, away_analysis)

    scale = 2.0
    xg_h = scale * hp + scale * 0.5 * dp
    xg_a = scale * ap + scale * 0.5 * dp

    if home_adj:
        for dim, pct in home_adj.items():
            if pct != 0:
                xg_h *= (1.0 + pct / 100.0 * 0.25)
    if away_adj:
        for dim, pct in away_adj.items():
            if pct != 0:
                xg_a *= (1.0 + pct / 100.0 * 0.25)

    return max(0.3, min(4.5, xg_h)), max(0.3, min(4.5, xg_a))


def _poisson_prob(k: int, lam: float) -> float:
    """泊松分布概率 P(X=k)"""
    return (lam ** k) * math.exp(-lam) / math.factorial(k)


def _poisson_sample(lam: float) -> int:
    """泊松采样"""
    L = math.exp(-lam)
    k = 0
    p = 1.0
    while True:
        p *= random.random()
        if p <= L:
            return k
        k += 1


def run_simulation(
    home_analysis: SixDimensionAnalysis,
    away_analysis: SixDimensionAnalysis,
    params: Optional[SimulationParams] = None,
) -> SimulationResult:
    """蒙特卡洛模拟比赛结果

    使用泊松分布对进球数建模，根据6维评分估算期望进球。
    """
    if params is None:
        params = SimulationParams()

    n = params.n_simulations
    home_adj = params.home_adjustments or {}
    away_adj = params.away_adjustments or {}

    xg_home, xg_away = _rating_to_xg_pair(home_analysis, away_analysis, home_adj, away_adj)

    home_wins = 0
    draws = 0
    away_wins = 0
    score_counter: Counter[str] = Counter()

    for _ in range(n):
        gh = _poisson_sample(xg_home)
        ga = _poisson_sample(xg_away)
        score_key = f"{gh}-{ga}"

        if gh > ga:
            home_wins += 1
        elif gh < ga:
            away_wins += 1
        else:
            draws += 1

        if n <= 50000:
            score_counter[score_key] += 1

    total_probs = {}
    if score_counter:
        total = sum(score_counter.values())
        for k, v in score_counter.most_common(15):
            total_probs[k] = round(v / total, 4)

    most_likely = max(total_probs, key=total_probs.get) if total_probs else "0-0"

    return SimulationResult(
        home_win_prob=round(home_wins / n, 3),
        draw_prob=round(draws / n, 3),
        away_win_prob=round(away_wins / n, 3),
        expected_goals_home=round(xg_home, 2),
        expected_goals_away=round(xg_away, 2),
        score_probs=total_probs,
        most_likely_score=most_likely,
        n_simulations=n,
    )


def expected_score_probabilities(home_xg: float, away_xg: float, max_goals: int = 6) -> dict[str, float]:
    """纯解析计算比分概率（不采样，快速准确）"""
    probs = {}
    for gh in range(max_goals + 1):
        for ga in range(max_goals + 1):
            p = _poisson_prob(gh, home_xg) * _poisson_prob(ga, away_xg)
            if p > 0.001:
                probs[f"{gh}-{ga}"] = round(p, 4)
    return dict(sorted(probs.items(), key=lambda x: -x[1])[:15])
