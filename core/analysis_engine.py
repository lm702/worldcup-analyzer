"""
6维名单分析引擎 v2 — 校准版
"""
import math
from datetime import datetime

from core.models import Squad, Player, Position, DimensionRating, SixDimensionAnalysis
from utils.config import DIMENSION_WEIGHTS
from core.models import position_category


# ─── 位置分布 ───────────────────────────────────────────

def _calc_position_distribution(squad: Squad) -> DimensionRating:
    cats = squad.count_by_category()
    strengths: list[str] = []
    weaknesses: list[str] = []
    evidence: dict[str, float] = {}

    targets = {"GK": 3, "DEF": 9, "MID": 6, "FWD": 5}
    total_penalty = 0.0

    for cat, target in targets.items():
        actual = cats.get(cat, 0)
        diff = abs(actual - target)
        evidence[f"{cat}_count"] = float(actual)
        if diff == 0:
            strengths.append(f"{cat}{actual}人，配置完美")
        elif diff == 1:
            if actual > target:
                weaknesses.append(f"{cat}{actual}人，冗余1人")
            else:
                weaknesses.append(f"{cat}{actual}人，缺1人")
            total_penalty += 5
        elif diff == 2:
            weaknesses.append(f"{cat}{actual}人，偏离{target}人")
            total_penalty += 10
        else:
            weaknesses.append(f"{cat}仅{actual}人，严重偏离{target}人")
            total_penalty += 18

    multi_pos = sum(1 for p in squad.players if len(p.secondary_positions) > 0)
    evidence["multi_position"] = float(multi_pos)
    if multi_pos >= 4:
        strengths.append(f"{multi_pos}人多面手，战术灵活")
        total_penalty -= 8
    elif multi_pos <= 1:
        weaknesses.append("多面手不足，变阵受限")
        total_penalty += 6

    raw_score = max(30, 85 - total_penalty)
    return DimensionRating(score=round(raw_score, 1), strengths=strengths, weaknesses=weaknesses, evidence=evidence)


# ─── 疲劳管理 ───────────────────────────────────────────

def _calc_fatigue_management(squad: Squad) -> DimensionRating:
    strengths: list[str] = []
    weaknesses: list[str] = []
    evidence: dict[str, float] = {}
    penalty = 0.0

    ages = [p.age for p in squad.players]
    avg_age = sum(ages) / len(ages)
    evidence["avg_age"] = round(avg_age, 1)

    over_30 = sum(1 for a in ages if a > 30)
    under_23 = sum(1 for a in ages if a < 23)
    evidence["over_30"] = float(over_30)
    evidence["under_23"] = float(under_23)

    if 25 <= avg_age <= 28:
        strengths.append(f"平均年龄{avg_age:.1f}岁，处于黄金期")
        penalty -= 8
    elif 28 < avg_age <= 30:
        strengths.append(f"平均年龄{avg_age:.1f}岁")
        penalty += 3
    elif avg_age > 30:
        weaknesses.append(f"平均年龄{avg_age:.1f}岁，偏大")
        penalty += 12
    else:
        penalty += 5

    if over_30 >= 8:
        weaknesses.append(f"{over_30}人超30岁，淘汰赛体能严重存疑")
        penalty += 22
    elif over_30 >= 6:
        weaknesses.append(f"{over_30}人超30岁，体能存疑")
        penalty += 14
    elif over_30 >= 4:
        weaknesses.append(f"{over_30}人超30岁")
        penalty += 6
    elif over_30 <= 2:
        strengths.append(f"仅{over_30}人超30岁，年龄结构健康")
        penalty -= 6

    if under_23 >= 5:
        strengths.append(f"{under_23}名U23新星")
        penalty -= 4
    elif under_23 <= 1:
        weaknesses.append("年轻血液不足")
        penalty += 4

    starters = squad.starters()
    if starters:
        avg_s_age = sum(p.age for p in starters) / len(starters)
        evidence["starter_avg_age"] = round(avg_s_age, 1)
        if avg_s_age > 30:
            weaknesses.append(f"主力均龄{avg_s_age:.1f}岁，偏高")
            penalty += 10
        elif avg_s_age <= 27:
            strengths.append(f"主力阵容年龄合理({avg_s_age:.1f}岁)")

    raw_score = max(10, min(100, 70 - penalty))
    return DimensionRating(score=round(raw_score, 1), strengths=strengths, weaknesses=weaknesses, evidence=evidence)


# ─── 淘汰赛适应性 ─────────────────────────────────────

def _calc_knockout_adaptability(squad: Squad) -> DimensionRating:
    strengths: list[str] = []
    weaknesses: list[str] = []
    evidence: dict[str, float] = {}
    bonus = 0.0

    total_caps = squad.total_caps
    evidence["total_caps"] = float(total_caps)

    if total_caps >= 1000:
        strengths.append(f"总出场{total_caps}次，经验碾压")
        bonus += 28
    elif total_caps >= 800:
        strengths.append(f"总出场{total_caps}次，经验极丰富")
        bonus += 20
    elif total_caps >= 600:
        strengths.append(f"总出场{total_caps}次，经验丰富")
        bonus += 12
    elif total_caps >= 400:
        strengths.append(f"总出场{total_caps}次")
        bonus += 5
    elif total_caps >= 250:
        bonus += 1
    else:
        weaknesses.append(f"总出场仅{total_caps}次，经验严重不足")
        bonus -= 18

    star_count = len(squad.stars)
    evidence["star_count"] = float(star_count)
    if star_count >= 6:
        strengths.append(f"{star_count}名球星压阵，关键战有依靠")
        bonus += 18
    elif star_count >= 4:
        strengths.append(f"{star_count}名球星")
        bonus += 10
    elif star_count >= 2:
        strengths.append(f"{star_count}名球星")
        bonus += 5
    elif star_count == 1:
        bonus += 2
    else:
        weaknesses.append("缺乏顶级球星")
        bonus -= 12

    high_caps = sum(1 for p in squad.players if p.caps >= 50)
    evidence["high_caps_50"] = float(high_caps)
    if high_caps >= 10:
        strengths.append(f"{high_caps}人出场50+，底蕴深厚")
        bonus += 10
    elif high_caps >= 7:
        strengths.append(f"{high_caps}人出场50+")
        bonus += 5
    elif high_caps <= 3:
        weaknesses.append(f"仅{high_caps}人出场50+")
        bonus -= 10

    raw_score = max(10, min(95, 40 + bonus))
    return DimensionRating(score=round(raw_score, 1), strengths=strengths, weaknesses=weaknesses, evidence=evidence)


# ─── 场地适应 ─────────────────────────────────────────

NA_KEYWORDS = ["MLS", "Liga MX", "美国", "墨西哥", "加拿大"]

NON_EURO_CLUBS = [
    "Flamengo", "Santos", "Gremio", "Botafogo", "Fenerbahce",
    "Zenit", "Al-Ahli", "Al-Ittihad", "Al-Ettifaq", "Gaziantep",
    "Pafos", "Astana", "Slovan Liberec", "Viktoria Plzen",
    "Jagiellonia", "Universitatea", "HNK Rijeka", "Slaven Belupo",
    "Karlsruher", "Schalke", "Young Boys",
]

TOP5_CLUBS = [
    "Liverpool", "Arsenal", "Manchester United", "Newcastle",
    "Chelsea", "Tottenham", "Manchester City", "Aston Villa",
    "Nottingham", "Sunderland", "Brentford", "Everton", "Leeds",
    "Real Madrid", "Barcelona", "Atletico", "Real Betis", "Sevilla", "Valencia",
    "Bayern", "Borussia Dortmund", "Gladbach", "Mainz",
    "Eintracht Frankfurt", "VfB Stuttgart", "Augsburg", "Freiburg", "Bayer",
    "PSG", "Monaco", "Lyon", "Rennes", "Lorient", "Lens", "Marseille", "Nice",
    "Inter Milan", "AC Milan", "Juventus", "Roma", "Atalanta",
    "Bologna", "Napoli", "Lazio", "Fiorentina", "Pisa",
    "Sassuolo", "Sampdoria", "Torino",
    "Benfica", "Sporting", "Porto",
    "PSV", "Ajax",
    "Celtic", "Rangers",
    "Dinamo Zagreb", "RB Salzburg",
]


def _calc_venue_adaptation(squad: Squad) -> DimensionRating:
    strengths: list[str] = []
    weaknesses: list[str] = []
    evidence: dict[str, float] = {}
    score = 65.0

    na = sum(1 for p in squad.players
             if any(kw.lower() in (p.club or "").lower() for kw in NA_KEYWORDS))
    evidence["na_experience"] = float(na)

    if na >= 2:
        strengths.append(f"{na}人有北美联赛经历")
        score += 12
    elif na == 1:
        score += 4
    else:
        weaknesses.append("无北美联赛经历")
        score -= 8

    non_eu = sum(1 for p in squad.players
                 if any(kw.lower() in (p.club or "").lower() for kw in NON_EURO_CLUBS))
    evidence["non_europe"] = float(non_eu)
    if non_eu >= 6:
        strengths.append(f"{non_eu}人在非欧洲联赛踢球")
        score += 6

    top5 = sum(1 for p in squad.players
               if any(kw.lower() in (p.club or "").lower() for kw in TOP5_CLUBS))
    evidence["top5_league"] = float(top5)
    if top5 >= 18:
        strengths.append(f"{top5}人在五大联赛")
        score += 8
    elif top5 >= 12:
        score += 4
    elif top5 <= 5:
        weaknesses.append(f"仅{top5}人在五大联赛")
        score -= 12

    return DimensionRating(score=round(max(10, min(95, score)), 1), strengths=strengths, weaknesses=weaknesses, evidence=evidence)


# ─── 换人策略 ─────────────────────────────────────────

def _calc_substitution_strategy(squad: Squad) -> DimensionRating:
    strengths: list[str] = []
    weaknesses: list[str] = []
    evidence: dict[str, float] = {}
    score = 60.0

    backups = squad.backups()
    fringe = squad.fringe()
    bench = backups + fringe

    if bench:
        avg_r = sum(p.season_rating for p in bench) / len(bench)
        evidence["bench_avg_rating"] = round(avg_r, 2)
        if avg_r >= 7.0:
            strengths.append(f"替补均评{avg_r:.2f}，深度优秀")
            score += 16
        elif avg_r >= 6.5:
            strengths.append(f"替补均评{avg_r:.2f}")
            score += 6
        elif avg_r < 6.0:
            weaknesses.append(f"替补均评仅{avg_r:.2f}")
            score -= 12

    multi = sum(1 for p in squad.players if len(p.secondary_positions) > 0)
    evidence["multi_position"] = float(multi)
    if multi >= 4:
        strengths.append(f"{multi}名多面手")
        score += 10
    elif multi <= 1:
        weaknesses.append("多面手不足")
        score -= 8

    bench_stars = sum(1 for p in bench if p.is_star)
    evidence["bench_stars"] = float(bench_stars)
    if bench_stars >= 2:
        strengths.append(f"替补席{bench_stars}名球星级")
        score += 8

    if len(bench) >= 15:
        strengths.append(f"{len(bench)}名轮换/边缘球员")
        score += 4
    elif len(bench) <= 11:
        weaknesses.append(f"仅{len(bench)}名轮换球员")
        score -= 5

    return DimensionRating(score=round(max(10, min(95, score)), 1), strengths=strengths, weaknesses=weaknesses, evidence=evidence)


# ─── 黄牌风险 ─────────────────────────────────────────

def _calc_yellow_card_risk(squad: Squad) -> DimensionRating:
    strengths: list[str] = []
    weaknesses: list[str] = []
    evidence: dict[str, float] = {}
    score = 70.0

    total_yc = sum(p.yellow_cards_24 for p in squad.players)
    avg_yc = total_yc / max(1, len(squad.players))
    evidence["avg_yellow"] = round(avg_yc, 2)

    if avg_yc <= 2.5:
        strengths.append(f"纪律性好(场均{avg_yc:.2f}张)")
        score += 18
    elif avg_yc <= 3.5:
        score += 5
    elif avg_yc <= 4.5:
        weaknesses.append(f"纪律性一般({avg_yc:.2f})")
        score -= 8
    else:
        weaknesses.append(f"纪律性差({avg_yc:.2f})")
        score -= 18

    def_pos = {Position.CB, Position.LB, Position.RB, Position.WB, Position.DM}
    def_players = [p for p in squad.players if p.position in def_pos]
    if def_players:
        def_avg = sum(p.yellow_cards_24 for p in def_players) / len(def_players)
        evidence["defender_avg_yc"] = round(def_avg, 2)
        if def_avg >= 4.0:
            weaknesses.append(f"防守球员吃牌多(均{def_avg:.2f})，停赛风险")
            score -= 12
        elif def_avg <= 2.0:
            strengths.append("防守球员纪律性好")

    high_risk = sum(1 for p in squad.players if p.yellow_cards_24 >= 5)
    evidence["high_risk"] = float(high_risk)
    if high_risk >= 5:
        weaknesses.append(f"{high_risk}人吃牌偏多")
        score -= 10
    elif high_risk >= 3:
        weaknesses.append(f"{high_risk}人吃牌偏多")
        score -= 4

    return DimensionRating(score=round(max(10, min(95, score)), 1), strengths=strengths, weaknesses=weaknesses, evidence=evidence)


# ─── 主入口 ─────────────────────────────────────────────

def analyze_squad(squad: Squad) -> SixDimensionAnalysis:
    dims = {
        "position_distribution": _calc_position_distribution(squad),
        "fatigue_management": _calc_fatigue_management(squad),
        "knockout_adaptability": _calc_knockout_adaptability(squad),
        "venue_adaptation": _calc_venue_adaptation(squad),
        "substitution_strategy": _calc_substitution_strategy(squad),
        "yellow_card_risk": _calc_yellow_card_risk(squad),
    }

    overall = sum(dims[k].score * DIMENSION_WEIGHTS.get(k, 1/6) for k in DIMENSION_WEIGHTS)

    return SixDimensionAnalysis(
        team_name=squad.team_name,
        position_distribution=dims["position_distribution"],
        fatigue_management=dims["fatigue_management"],
        knockout_adaptability=dims["knockout_adaptability"],
        venue_adaptation=dims["venue_adaptation"],
        substitution_strategy=dims["substitution_strategy"],
        yellow_card_risk=dims["yellow_card_risk"],
        overall_rating=round(overall, 1),
        analyzed_at=datetime.now().isoformat(),
    )


def compare_teams(squad_a: Squad, squad_b: Squad) -> tuple[SixDimensionAnalysis, SixDimensionAnalysis]:
    return analyze_squad(squad_a), analyze_squad(squad_b)
