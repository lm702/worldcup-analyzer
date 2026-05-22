from pydantic import BaseModel, Field, model_validator
from enum import StrEnum
from typing import Optional


class Position(StrEnum):
    GK = "GK"
    CB = "CB"
    LB = "LB"
    RB = "RB"
    WB = "WB"
    DM = "DM"
    CM = "CM"
    AM = "AM"
    LW = "LW"
    RW = "RW"
    ST = "ST"
    CF = "CF"


POSITION_CATEGORY_MAP: dict[str, tuple[Position, ...]] = {
    "GK": (Position.GK,),
    "DEF": (Position.CB, Position.LB, Position.RB, Position.WB),
    "MID": (Position.DM, Position.CM, Position.AM),
    "FWD": (Position.LW, Position.RW, Position.ST, Position.CF),
}


def position_category(pos: Position) -> str:
    for cat, members in POSITION_CATEGORY_MAP.items():
        if pos in members:
            return cat
    return "FWD"


class Player(BaseModel):
    name: str
    position: Position
    secondary_positions: list[Position] = Field(default_factory=list)
    club: str = ""
    league: str = ""
    age: int = Field(ge=16, le=45)
    caps: int = Field(default=0, ge=0)
    goals: int = Field(default=0, ge=0)
    is_star: bool = False
    is_injured: bool = False
    yellow_cards_24: int = Field(default=0, ge=0)
    minutes_24: int = Field(default=0, ge=0)
    depth_rank: int = Field(default=2, ge=1, le=3)
    season_rating: float = Field(default=6.5, ge=1.0, le=10.0)


class Squad(BaseModel):
    team_name: str
    group: str = ""
    coach: str = ""
    players: list[Player] = Field(min_length=26, max_length=26)
    updated_at: str = ""

    @model_validator(mode="after")
    def validate_squad_size(self):
        if len(self.players) != 26:
            raise ValueError(f"必须恰好26名球员，当前{len(self.players)}人")
        return self

    def count_by_position(self) -> dict[Position, int]:
        counts: dict[Position, int] = {}
        for p in self.players:
            counts[p.position] = counts.get(p.position, 0) + 1
        return counts

    def count_by_category(self) -> dict[str, int]:
        result: dict[str, int] = {}
        for p in self.players:
            cat = position_category(p.position)
            result[cat] = result.get(cat, 0) + 1
        return result

    def starters(self) -> list[Player]:
        return [p for p in self.players if p.depth_rank == 1]

    def backups(self) -> list[Player]:
        return [p for p in self.players if p.depth_rank == 2]

    def fringe(self) -> list[Player]:
        return [p for p in self.players if p.depth_rank == 3]

    @property
    def avg_age(self) -> float:
        return sum(p.age for p in self.players) / len(self.players)

    @property
    def total_caps(self) -> int:
        return sum(p.caps for p in self.players)

    @property
    def stars(self) -> list[Player]:
        return [p for p in self.players if p.is_star]


class DimensionRating(BaseModel):
    score: float = Field(ge=0, le=100)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    evidence: dict[str, float] = Field(default_factory=dict)


class SixDimensionAnalysis(BaseModel):
    team_name: str
    position_distribution: DimensionRating = Field(default_factory=DimensionRating)
    fatigue_management: DimensionRating = Field(default_factory=DimensionRating)
    knockout_adaptability: DimensionRating = Field(default_factory=DimensionRating)
    venue_adaptation: DimensionRating = Field(default_factory=DimensionRating)
    substitution_strategy: DimensionRating = Field(default_factory=DimensionRating)
    yellow_card_risk: DimensionRating = Field(default_factory=DimensionRating)
    overall_rating: float = Field(default=50.0, ge=0, le=100)
    analyzed_at: str = ""

    def dimension_list(self) -> list[tuple[str, DimensionRating]]:
        return [
            ("位置分布", self.position_distribution),
            ("疲劳管理", self.fatigue_management),
            ("淘汰赛适应性", self.knockout_adaptability),
            ("场地适应", self.venue_adaptation),
            ("换人策略", self.substitution_strategy),
            ("黄牌风险", self.yellow_card_risk),
        ]


class OddsSource(StrEnum):
    BET365 = "BET365"
    FANDUEL = "FanDuel"
    WILLIAM_HILL = "WilliamHill"
    OTHER = "Other"


class MoneylineOdds(BaseModel):
    home_win: float = Field(gt=1.0)
    draw: float = Field(gt=1.0)
    away_win: float = Field(gt=1.0)


class AsianHandicap(BaseModel):
    line: float
    home_odds: float = Field(gt=1.0)
    away_odds: float = Field(gt=1.0)


class OverUnder(BaseModel):
    line: float
    over_odds: float = Field(gt=1.0)
    under_odds: float = Field(gt=1.0)


class MatchOdds(BaseModel):
    source: OddsSource = OddsSource.BET365
    moneyline: Optional[MoneylineOdds] = None
    asian_handicap: Optional[AsianHandicap] = None
    over_under: Optional[OverUnder] = None
    updated_at: str = ""


class Match(BaseModel):
    match_id: str
    home_team: str
    away_team: str
    group: str = ""
    stage: str = "group"
    match_date: str = ""
    venue: str = ""
    odds_list: list[MatchOdds] = Field(default_factory=list)


class ValueBet(BaseModel):
    market_type: str
    selection: str
    odds: float
    implied_prob: float
    model_prob: float
    expected_value: float
    kelly_fraction: float
    confidence: str = "low"
    recommendation: str = "观望"


class SimulationParams(BaseModel):
    home_adjustments: dict[str, float] = Field(default_factory=dict)
    away_adjustments: dict[str, float] = Field(default_factory=dict)
    n_simulations: int = Field(default=10000, ge=100, le=100000)


class SimulationResult(BaseModel):
    home_win_prob: float = 0.0
    draw_prob: float = 0.0
    away_win_prob: float = 0.0
    expected_goals_home: float = 0.0
    expected_goals_away: float = 0.0
    score_probs: dict[str, float] = Field(default_factory=dict)
    most_likely_score: str = "0-0"
    n_simulations: int = 0
