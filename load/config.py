from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Thu muc du lieu raw
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
SEASONS = [
    int(s.strip()) for s in os.getenv("SEASONS", "2023,2024,2025,2026").split(",") if s.strip()
]

# Cau hinh Postgres Connection
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "epl")
POSTGRES_USER = os.getenv("POSTGRES_USER", "root")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "root")

POSTGRES_URL = f"jdbc:postgresql://{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
POSTGRES_DRIVER = "org.postgresql.Driver"

PYSPARK_POSTGRES_CONFIG = {
    "url": POSTGRES_URL,
    "user": POSTGRES_USER,
    "password": POSTGRES_PASSWORD,
    "driver": POSTGRES_DRIVER,
}

PSYCOPG2_POSTGRES_CONFIG = {
    "host": POSTGRES_HOST,
    "port": POSTGRES_PORT,
    "dbname": POSTGRES_DB,
    "user": POSTGRES_USER,
    "password": POSTGRES_PASSWORD,
}

# Magic numbers
EPL_MATCHES_TOTAL = 380