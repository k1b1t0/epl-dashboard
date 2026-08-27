# 📥 Ingestion Module Documentation

## 📌 Overview
This module extracts football data (EPL specified) from football-data, remove unnecessary and add necessary fields then save them to Data Lake (local Parquet files). 

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
- Add football-data API token to `.env` (optional) 
```
FOOTBALL_DATA_TOKEN=...
```
- Command
```bash
uv run python -m ingestion.rest_api_football_pipeline
```

---

## 🧠 Logic
- Only parse if the season isn't finished (`matches_full` file doesn't exist)
- Parse data from REST API
- Remove unnecessary fields
- Add `season` field
- Write into parquet file in `data/raw/{season}/`