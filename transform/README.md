# ⚽ Transform Module Documentation

This project contains the **dbt** transformation layer for the EPL data. It transforms raw ingestion data into a clean, normalized, and performant **Star Schema (Data Marts)** for dashboard.

---

## 🏛️ Architecture

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
   ├── int_team_matches       (Doubles matches into records for each team (Home/Away))
   ├── int_current_standings  (Final or current standings for every seasons)
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
- 1-1 Mapping from raw source tables, change column names.
- `stg_matches.sql`
- `stg_matches_referees.sql`
- `stg_teams.sql`
- `stg_teams_squad.sql`

### 2. Intermediate Layer (`models/intermediate/`)
- Using data from staging tables and perform heavy computation.
- `int_team_matches.sql`
- `int_current_standings.sql`
- `int_matchday_standings.sql`
- `int_history_standings.sql`

### 3. Data Marts Layer (`models/marts/`)
- Final result table following Star Model, ready for BI, data analyze and visualization.
- `dim_teams.sql`
- `fct_current_standings.sql`
- `fct_matchday_standings.sql`
- `fct_history_standings.sql`
- `fct_team_matches.sql`

---

## 🛠️ Custom Macros (`macros/`)
- `get_points_earned.sql`
- `get_match_result.sql`

---

## 🧪 Data Quality Tests

### 1. Custom Singular Tests (`tests/`)
- `assert_finished_matches_have_scores.sql`
- `assert_unfinished_matches_no_scores.sql`

### 2. Generic Schema Tests (`models/staging/schema.yml`)
- `unique`
- `not_null`

---

## 🚀 How to Run

### 1. Execute Transformation Pipeline
```bash
cd transform/

# Run all models across all layers
uv run dbt run

# Run a specific layer
uv run dbt run --select staging
uv run dbt run --select intermediate
uv run dbt run --select marts
```

### 2. Run Data Quality Tests
```bash
cd transform/
uv run dbt test
```

### 3. Generate & View Interactive Lineage Docs
```bash
cd transform/
uv run dbt docs generate
uv run dbt docs serve
```
