# ⚡ Load Module Documentation

## 📌 Overview
This module loads data from Data Lake (Parquet files) to DWH (PostgreSQL). It reads data from each season, then deduplicates the records and update the DWH.
It also checks whether the season is finished (all 380 matches have `FINISHED` status) then create a `matches_full` file to finalize the season.

---

## 🛠️ Tech Stack & Logic
- **Engine**: Apache Spark (PySpark)
- **JDBC Driver**: PostgreSQL JDBC Driver (`org.postgresql:postgresql:42.7.3`)
- **Deduplication Strategy**: Window partitioning by entity ID (`partitionBy("id").orderBy(col("last_updated").desc())`).

---

## 🔑 Key Scripts
- `parquet_to_postgres_pipeline.py`: Main PySpark loading script.

---

## 📝 Usage / Manual Execution
```bash
uv run python -m load.parquet_to_postgres_pipeline
```
---

## 🧠 Logic
- Ignore the finished season
- Read every .parquet files from a season then deduplicate by ID, only keep the newest record
- If the season is over, then finalize a `matches_full` file

## 🗄️ Target DWH Tables
- `raw_matches`
- `raw_matches_referees`
- `raw_teams`
- `raw_teams_squad`