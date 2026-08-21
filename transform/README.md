# ⚽ EPL Data Transformation with dbt (epl_transform)

This project contains the **dbt (data build tool)** transformation layer for the English Premier League (EPL) Data Pipeline. It transforms raw ingestion data from PostgreSQL into a clean, normalized, and performant **Star Schema (Data Marts)** designed for analytical dashboards and Business Intelligence.

---

## 🏛️ Architecture & Data Lineage

The transformation follows standard dbt multi-layered architecture:

```
Sources (epl.public)
   ├── raw_matches
   ├── raw_matches_referees
   ├── raw_teams
   └── raw_teams_squad
        │
        ▼
   [ 1. Staging Layer (Views) ]
   ├── stg_matches
   ├── stg_matches_referees
   ├── stg_teams
   └── stg_teams_squad
        │
        ▼
   [ 2. Intermediate Layer (Tables) ]
   ├── int_team_matches       (Doubles matches into Home/Away team rows with primary key team_match_id)
   ├── int_current_standings  (Aggregates overall season totals & ranks teams)
   ├── int_matchday_standings (Cumulative standings per season & matchday 1..38)
   └── int_history_standings  (Timeline cumulative standings partitioned by season & played count)
        │
        ▼
   [ 3. Marts Layer (Tables - Star Schema) ]
   ├── dim_teams              (Deduplicated team metadata & stadium info)
   ├── fct_current_standings  (Season-end / Latest standings joined with dim_teams)
   ├── fct_matchday_standings (Matchday-by-matchday standings joined with dim_teams)
   ├── fct_history_standings  (Game-by-game cumulative standings joined with dim_teams)
   └── fct_team_matches       (Full match history joined with team & opponent details)
```

---

## 📂 Project Structure & Models Overview

### 1. Staging Layer (`models/staging/`)
- **`stg_matches.sql`**: Standardizes raw match results, explicitly casts timestamps, scorelines, and renames `status` to `match_status`.
- **`stg_matches_referees.sql`**: Cleans referee assignment data per match.
- **`stg_teams.sql`**: Normalizes club profile information (TLA, crest, address, venue, founded year).
- **`stg_teams_squad.sql`**: Cleans player squad profiles, aliasing `date_of_birth` to `dob`.

### 2. Intermediate Layer (`models/intermediate/`)
- **`int_team_matches.sql`**: Pivots match records into two rows (Home perspective & Away perspective) with surrogate key `team_match_id`.
- **`int_current_standings.sql`**: Aggregates points, wins, draws, losses, goal differences and calculates `dense_rank()` per season.
- **`int_matchday_standings.sql`**: Uses window functions `SUM(...) OVER (PARTITION BY season, team_id ORDER BY matchday)` to calculate cumulative matchday standings ($1 \rightarrow 38$).
- **`int_history_standings.sql`**: Calculates cumulative standings ordered by `utc_date` and ranks teams after completing $N$ games played (`PARTITION BY season, played`).

### 3. Data Marts Layer (`models/marts/`)
- **`dim_teams.sql`**: Master team dimension table deduplicated by `team_id`.
- **`fct_current_standings.sql`**: Latest season standings ready for dashboard KPIs.
- **`fct_matchday_standings.sql`**: Traditional matchday standings for league table progression charts.
- **`fct_history_standings.sql`**: Equal-games-played standings progression chart.
- **`fct_team_matches.sql`**: Full match results joined with both Team and Opponent logos/metadata for head-to-head analysis.

---

## 🛠️ Custom Macros (`macros/`)

- **`get_points_earned(goals_for, goals_against)`**: Returns `3` points for win, `1` for draw, `0` for loss.
- **`get_match_result(goals_for, goals_against)`**: Returns `'WIN'`, `'DRAW'`, or `'LOST'`.

---

## 🚀 How to Run

### 1. Execute Transformation Pipeline
```bash
# Run all models across all layers
uv run dbt run

# Run a specific layer
uv run dbt run --select staging
uv run dbt run --select intermediate
uv run dbt run --select marts
```

### 2. Run Data Quality Tests
```bash
uv run dbt test
```

### 3. Generate & View Interactive Lineage Docs
```bash
uv run dbt docs generate
uv run dbt docs serve
```
