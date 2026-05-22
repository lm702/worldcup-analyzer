import json
import os
from pathlib import Path
from typing import Optional

from core.models import Squad, SixDimensionAnalysis, Match, MatchOdds

DATA_DIR = Path(__file__).parent
TEAMS_DIR = DATA_DIR / "teams"
ANALYSIS_DIR = DATA_DIR / "analysis"
MATCHES_DIR = DATA_DIR / "matches"
ODDS_DIR = DATA_DIR / "odds"

for d in [TEAMS_DIR, ANALYSIS_DIR, MATCHES_DIR, ODDS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _read_json(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _team_path(team_name: str) -> Path:
    safe = team_name.lower().replace(" ", "_").replace("-", "_")
    return TEAMS_DIR / f"{safe}.json"


def list_team_names() -> list[str]:
    names = []
    for f in sorted(TEAMS_DIR.glob("*.json")):
        data = _read_json(f)
        if data and "team_name" in data:
            names.append(data["team_name"])
    return names


def save_squad(squad: Squad) -> None:
    path = _team_path(squad.team_name)
    _write_json(path, squad.model_dump(mode="json"))


def load_squad(team_name: str) -> Optional[Squad]:
    path = _team_path(team_name)
    data = _read_json(path)
    if data is None:
        return None
    return Squad(**data)


def delete_squad(team_name: str) -> None:
    path = _team_path(team_name)
    if path.exists():
        path.unlink()


def _analysis_path(team_name: str) -> Path:
    safe = team_name.lower().replace(" ", "_").replace("-", "_")
    return ANALYSIS_DIR / f"{safe}.json"


def save_analysis(analysis: SixDimensionAnalysis) -> None:
    path = _analysis_path(analysis.team_name)
    _write_json(path, analysis.model_dump(mode="json"))


def load_analysis(team_name: str) -> Optional[SixDimensionAnalysis]:
    path = _analysis_path(team_name)
    data = _read_json(path)
    if data is None:
        return None
    return SixDimensionAnalysis(**data)


def list_analysis_names() -> list[str]:
    names = []
    for f in sorted(ANALYSIS_DIR.glob("*.json")):
        data = _read_json(f)
        if data and "team_name" in data:
            names.append(data["team_name"])
    return names


def _match_path(match_id: str) -> Path:
    safe = match_id.replace(" ", "_").replace("-", "_").replace("/", "_")
    return MATCHES_DIR / f"{safe}.json"


def save_match(match: Match) -> None:
    path = _match_path(match.match_id)
    _write_json(path, match.model_dump(mode="json"))


def load_match(match_id: str) -> Optional[Match]:
    path = _match_path(match_id)
    data = _read_json(path)
    if data is None:
        return None
    return Match(**data)


def list_match_ids() -> list[str]:
    ids = []
    for f in sorted(MATCHES_DIR.glob("*.json")):
        data = _read_json(f)
        if data and "match_id" in data:
            ids.append(data["match_id"])
    return ids
