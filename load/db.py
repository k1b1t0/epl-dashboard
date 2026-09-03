import psycopg2
from pyspark.sql import SparkSession

from load.config import PYSPARK_POSTGRES_CONFIG, PSYCOPG2_POSTGRES_CONFIG

def execute_sql(sql: str) -> None:
    conn = psycopg2.connect(**PSYCOPG2_POSTGRES_CONFIG)
    try:
        with conn, conn.cursor() as cur:
            cur.execute(sql)
            print(f"Executed SQL: {sql} | Affected rows: {cur.rowcount}")
    except Exception as e:
        conn.rollback()
        print(f"SQL execution error: {e}")
        raise
    finally:
        conn.close()

def read_from_postgres(spark: SparkSession, sql: str):
    return spark.read \
        .format("jdbc") \
        .options(**PYSPARK_POSTGRES_CONFIG) \
        .option("dbtable", sql) \
        .load()

def write_to_postgres(df, table_name: str, mode: str = "append") -> None:
    df.write \
        .format("jdbc") \
        .options(**PYSPARK_POSTGRES_CONFIG) \
        .option("dbtable", table_name) \
        .mode(mode) \
        .save()

# TODO: Su dung PySpark de ghi vao bang staging, sau do upsert bang psycopg2
# Hien tai: xoa roi append
def upsert_to_postgres(df, target_table:str, season:int) -> None:
    execute_sql(f"DELETE FROM {target_table} WHERE season = {season}")
    write_to_postgres(df, target_table, mode="append")

    