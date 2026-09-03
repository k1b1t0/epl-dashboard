from typing import Any
from pathlib import Path
import os
from datetime import datetime
from dotenv import load_dotenv

import dlt
from dlt.sources.rest_api import (
    RESTAPIConfig,
    rest_api_resources,
)

from .schemas import MATCHES_COLUMNS, TEAMS_COLUMNS

load_dotenv()

# API Token
FOOTBALL_DATA_TOKEN = os.getenv("FOOTBALL_DATA_TOKEN")

# Thu muc du lieu raw
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

# Cac mua giai can cao
SEASONS = [2023, 2024, 2025, 2026]

# Loc truong bang teams
def filter_team_fields(team: dict) -> dict:
    team.pop("runningCompetitions", None)
    team.pop("coach", None)
    team.pop("staff", None)

    if "area" in team and isinstance(team["area"], dict):
        team["area_id"] = team["area"].get("id")
        team.pop("area", None)

    return team

# Loc truong bang matches
def create_match_filter(season: int):
    def filter_match_fields(match: dict) -> dict:
        if "area" in match and isinstance(match["area"], dict):
            match["area_id"] = match["area"].get("id")
            match.pop("area", None)

        match.pop("season", None)
        match["season"] = season

        if match.get("referees"):
            match["referee_id"] = match["referees"][0].get("id")
            match["referee_name"] = match["referees"][0].get("name")

        match.pop("referees", None)

        match.pop("odds", None)
        return match
    return filter_match_fields

@dlt.source(name="football")
def football_source(season: int) -> Any:
    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://api.football-data.org/v4/",
            "headers": {"X-Auth-Token": FOOTBALL_DATA_TOKEN},
        },
        "resources": [
            {
                "name": "teams",
                "endpoint": {
                    "path": "competitions/PL/teams",
                    "params": {"season": season},
                    "data_selector": "teams",
                    "paginator": "single_page",
                },
                "columns": TEAMS_COLUMNS,
                "primary_key": "id",
                "write_disposition": "append",
            },
            {
                "name": "matches",
                "endpoint": {
                    "path": "competitions/PL/matches",
                    "params": {"season": season},
                    "data_selector": "matches",
                    "paginator": "single_page",
                },
                "columns": MATCHES_COLUMNS,
                "primary_key": "id",
                "write_disposition": "append",
            }
        ],
    }
    yield from rest_api_resources(config)

def load_football() -> None:
    for season in SEASONS:
        season_dir = RAW_DIR / str(season)
        season_dir.mkdir(parents=True, exist_ok=True)

        # Kiem tra file ton tai de bo qua
        has_matches_full = any(season_dir.glob("matches_full*.parquet"))
        has_teams = any(season_dir.glob("teams*.parquet"))

        resources = []
        if not has_teams:
            resources.append("teams")
        if not has_matches_full:
            resources.append("matches")

        if not resources:
            print(f"Season {season}: da co du file matches_full/teams, bo qua.")
            continue

        # Khoi tao source va apply filter
        source = football_source(season)
        if "teams" in resources:
            source.teams.add_map(filter_team_fields)
        if "matches" in resources:
            source.matches.add_map(create_match_filter(season))

        # Struct luu parquet theo timestamp
        ts = datetime.now().strftime("%y%m%d_%H%M%S")
        pipeline = dlt.pipeline(
            pipeline_name=f"football_{season}",
            destination=dlt.destinations.filesystem(
                bucket_url=str(season_dir),
                layout=f"../{{table_name}}_{ts}.{{ext}}"
            ),
        )

        load_info = pipeline.run(source.with_resources(*resources), loader_file_format="parquet")
        print(f"Season {season} loaded {resources}: {load_info}")

if __name__ == "__main__":
    load_football()

