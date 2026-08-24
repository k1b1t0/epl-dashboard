# 📥 Ingestion Module Documentation

## 📌 Overview
Briefly describe the purpose of the Ingestion module (e.g., fetching match fixtures, team metadata, and squad details from Football-Data.org API).

---

## 🛠️ Data Sources & Tools
- **API Endpoint**: `https://api.football-data.org/v4/`
- **Tool**: `dlt` (Data Loading Tool)
- **Output Storage Format**: Parquet files partitioned by season in `data/raw/{season}/`

---

## 🔑 Key Scripts & Components
- `rest_api_football_pipeline.py`: Main ingestion script.
- `schemas.py`: Column schemas and data structure definitions.

---

## 📝 Usage / Manual Execution
```bash
uv run python -m ingestion.rest_api_football_pipeline
```
