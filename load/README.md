# ⚡ Load Module Documentation

## 📌 Overview
Briefly describe the purpose of the Load module (e.g., reading Parquet data from Data Lake, deduplicating records using Window Functions, and loading clean raw tables into PostgreSQL DWH).

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
