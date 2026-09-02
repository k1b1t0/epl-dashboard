from pathlib import Path
import os
import sys
from dotenv import load_dotenv

from pyspark.sql import SparkSession
from pyspark.sql.window import Window
from pyspark.sql.functions import col, row_number, lit

load_dotenv()

# Thu muc du lieu raw
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
SEASONS = [2023, 2024, 2025, 2026]

# Cau hinh Postgres Connection
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "epl")
POSTGRES_USER = os.getenv("POSTGRES_USER", "root")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "root")

POSTGRES_URL = f"jdbc:postgresql://{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
POSTGRES_DRIVER = "org.postgresql.Driver"

def get_spark_session() -> SparkSession:
    return SparkSession.builder \
        .appName("EPL_Parquet_To_Postgres") \
        .config("spark.jars.packages", "org.postgresql:postgresql:42.7.3") \
        .config("spark.sql.shuffle.partitions", "4") \
        .getOrCreate()

import psycopg2

def execute_sql(sql: str) -> None:
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD
        )
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(sql)
            print(f"Executed SQL: {sql} | Affected rows: {cur.rowcount}")
        conn.close()
    except Exception as e:
        print(f"SQL execution error: {e}")

def read_from_postgres(spark: SparkSession, sql: str):
    return spark.read \
        .format("jdbc") \
        .option("url", POSTGRES_URL) \
        .option("dbtable", sql) \
        .option("user", POSTGRES_USER) \
        .option("password", POSTGRES_PASSWORD) \
        .option("driver", POSTGRES_DRIVER) \
        .load()

def write_to_postgres(df, table_name: str, mode: str = "append") -> None:
    df.write \
        .format("jdbc") \
        .option("url", POSTGRES_URL) \
        .option("dbtable", table_name) \
        .option("user", POSTGRES_USER) \
        .option("password", POSTGRES_PASSWORD) \
        .option("driver", POSTGRES_DRIVER) \
        .mode(mode) \
        .save()

def load_matches(spark, season, matches_full_file, season_dir, target_matches):
    match_files = [str(f) for f in season_dir.glob("matches_*.parquet")
                    if "referees" not in f.name and "full" not in f.name]
    
    if match_files and target_matches is None:
        print(f"Season {season}: Progress {len(match_files)} match files")
        raw_matches = spark.read.parquet(*match_files)
        match_window = Window.partitionBy("id").orderBy(
            col("last_updated").desc_nulls_last(),
            col("_dlt_load_id").desc_nulls_last()
        )

        target_matches = raw_matches \
            .withColumn("rn", row_number().over(match_window)) \
            .filter(col("rn") == 1) \
            .drop("rn")

    if target_matches is not None:
        execute_sql(f"DELETE FROM raw_matches WHERE season = {season}")
        write_to_postgres(target_matches, "raw_matches", mode="append")

        total = target_matches.count()
        unfinished = target_matches.filter(col("status") != "FINISHED").count()
        if total == 380 and unfinished == 0:
            
            print(f"Season {season}: season finished, saved to finished file")

            target_matches.toPandas().to_parquet(matches_full_file, index=False)

def load_teams_and_squad(spark, season, season_dir):
    team_files = [str(f) for f in season_dir.glob("teams_*.parquet") if "squad" not in f.name]
    if team_files:
        print(f"Season {season}: Process teams...")
        raw_season_teams = spark.read.parquet(*team_files)
        team_window = Window.partitionBy("id").orderBy(
            col("last_updated").desc_nulls_last(), 
            col("_dlt_load_id").desc_nulls_last()
        )
        dedup_season_teams = raw_season_teams.withColumn("rn", row_number() \
            .over(team_window)) \
            .filter(col("rn") == 1) \
            .drop("rn") \
            .withColumn("season", lit(season))

        execute_sql(f"DELETE FROM raw_teams WHERE season = {season}")
        write_to_postgres(dedup_season_teams, "raw_teams", mode="append")

    squad_files = [str(f) for f in season_dir.glob("teams__squad_*.parquet")]
    if squad_files and dedup_season_teams:
        print(f"Season {season}: Process squad...")
        raw_squad = spark.read.parquet(*squad_files)
        season_squad = raw_squad.join(
            dedup_season_teams.select(col("_dlt_id").alias("parent_id_key"), col("id").alias("team_id")),
            raw_squad._dlt_parent_id == col("parent_id_key"),
            "inner"
        ).drop("parent_id_key").withColumn("season", lit(season))

        execute_sql(f"DELETE FROM raw_teams_squad WHERE season = {season}")
        write_to_postgres(season_squad, "raw_teams_squad", mode="append")

def process_pipeline(spark: SparkSession):
    print("Start Load")

    for season in SEASONS:
        season_dir = RAW_DIR / str(season)
        if not season_dir.exists():
            continue

        print(f"Season {season}")

        
        matches_full_file = season_dir / f"matches_full_{season}.parquet"
        target_matches = None

        if matches_full_file.exists():
            print(f"Season {season} finsihed")

            # Check DWH
            check_matches_existed = read_from_postgres(
                spark, sql=f"(SELECT COUNT(*) FROM raw_matches WHERE season = {season}) as t"
            )
            count_val = check_matches_existed.first()[0]

            if count_val != 0:
                continue
            else:
                target_matches = spark.read.parquet(str(matches_full_file))

        # Matches
        load_matches(spark, season, matches_full_file, season_dir, target_matches)

        # Teams & Squads
        load_teams_and_squad(spark, season, season_dir)

    print("Finished Load")

def main():
    spark = get_spark_session()
    spark.sparkContext.setLogLevel("WARN")
    process_pipeline(spark)

if __name__ == "__main__":
    main()