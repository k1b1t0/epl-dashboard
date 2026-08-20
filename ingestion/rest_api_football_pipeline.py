from typing import Any, Optional
from pathlib import Path
import os
from dotenv import load_dotenv

import dlt
from dlt.sources.rest_api import (
    RESTAPIConfig,
    rest_api_resources,
)

load_dotenv()

# API Token
FOOTBALL_DATA_TOKEN = os.getenv("FOOTBALL_DATA_TOKEN")

# Directories
BASE_DIR = Path(__file__).resolve().parent.parent
DUCKDB_FILE = BASE_DIR / 'data' / 'raw' / 'duckdb' / 'football_raw.duckdb'

# Available seasons
SEASONS = [2023, 2024, 2025, 2026]

# Loc bo cac truong khong su dung
def filter_team_fields(team):
    team.pop("runningCompetitions", None)
    team.pop("coach", None)
    team.pop("staff", None)

    if "area" in team and isinstance(team["area"], dict):
        team["area_id"] = team["area"].get("id")
        team.pop("area", None)

    return team

def create_match_filter(season):
    def filter_match_fields(match):
        if "area" in match and isinstance(match["area"], dict):
            match["area_id"] = match["area"].get("id")
            match.pop("area", None)

        match.pop("season", None)
        match["season"] = season

        match.pop("odds", None)
        return match
    return filter_match_fields
    

@dlt.source(name="football")
def football_source(season) -> Any:
    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://api.football-data.org/v4/",
            "headers": {"X-Auth-Token": FOOTBALL_DATA_TOKEN},
        },
        "resources": [
            {
                "name": "epl_teams",
                "endpoint": {
                    "path": "competitions/PL/teams",
                    "params": {"season": season},
                    "data_selector": "teams",
                    "paginator": "single_page",
                },
                "primary_key": "id",
                "write_disposition": "merge",
            },
            {
                "name": "epl_matches",
                "endpoint": {
                    "path": "competitions/PL/matches",
                    "params": {"season": season},
                    "data_selector": "matches",
                    "paginator": "single_page",
                },
                "columns": {
                    "group": {"data_type": "text", "nullable": True} 
                },
                "primary_key": "id",
                "write_disposition": "merge",
            }
        ],
    }
    yield from rest_api_resources(config)

def load_football() -> None:
    pipeline = dlt.pipeline(
        pipeline_name="rest_duckdb_football",
        destination="duckdb",
        dataset_name="football",
    )

    for season in SEASONS:
        source = football_source(season)
        source.epl_matches.add_map(create_match_filter(season))
        source.epl_teams.add_map(filter_team_fields)
        load_info = pipeline.run(source)
        print(load_info)

if __name__ == "__main__":
    load_football()
