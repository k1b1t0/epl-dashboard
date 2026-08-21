from dlt.common import configuration
from ingestion.rest_api_football_pipeline import RAW_DIR
import pyspark
from pyspark.sql import SparkSession
from pathlib import Path

spark = SparkSession.builder \
    .master("local[*]") \
    .appName("test") \
    .config("spark.jars.packages", "org.postgresql:postgresql:42.7.3") \
    .getOrCreate()

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
SEASONS = [2023, 2024, 2025, 2026]

# Ket noi PySpark - Postgres
url = "jdbc:postgresql://localhost:5432/epl"

properties = {
    "user": "root",
    "password": "root",
    "driver": "org.postgresql.Driver"
}

# PySpark doc file tung mua va ghep vao
for season in SEASONS:
    season_dir = RAW_DIR / str(season)

    # Kiem tra matches_full
    has_matches_full = any(season_dir.glob("matches_full*.parquet"))

    if has_matches_full:
        continue

    