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

def execute_jdbc_sql(spark: SparkSession, sql: str) -> None:
    try:
        driver_mgr = spark._sc._gateway.jvm.java.sql.DriverManager
        conn = driver_mgr.getConnection(POSTGRES_URL, POSTGRES_USER, POSTGRES_PASSWORD)
        stmt = conn.createStatement()
        stmt.executeUpdate(sql)
        stmt.close()
        conn.close()
    except Exception as e:
        print(f'JDBC error: {e}')
        pass

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

def process_pipeline(spark: SparkSession):
    print("Start Load")

    for season in SEASONS:
        season_dir = RAW_DIR / str(season)
        if not season_dir.exists():
            continue

        print(f"Season {season}")

        # 1. Matches & Referees
        matches_full_file = season_dir / "matches_full.parquet"
        target_matches = None

        if matches_full_file.exists():
            print(f"Season {season}: Da chot matches_full.parquet")
            check_matches_existed = read_from_postgres(
                spark, sql=f"(SELECT COUNT(*) FROM raw_matches WHERE season = {season}) as t"
            )
            count_val = check_matches_existed.first()[0]
            if count_val == 0:
                print(f"Season {season}: Postgres trong -> Nap tu matches_full.parquet...")
                target_matches = spark.read.parquet(str(matches_full_file))
        else:
            match_files = [str(f) for f in season_dir.glob("matches_*.parquet")
                           if "referees" not in f.name and "full" not in f.name]
            if match_files:
                print(f"Season {season}: Process {len(match_files)} matches snapshot files...")
                raw_matches = spark.read.parquet(*match_files)
                match_window = Window.partitionBy("id").orderBy(
                    col("last_updated").desc_nulls_last(), 
                    col("_dlt_load_id").desc_nulls_last()
                )
                target_matches = raw_matches.withColumn("rn", row_number().over(match_window)).filter(col("rn") == 1).drop("rn")

                # Chot matches_full neu tat ca tran da FINISHED
                total = target_matches.count()
                unfinished = target_matches.filter(col("status") != "FINISHED").count()
                if total > 0 and unfinished == 0:
                    print(f"Season {season}: Tat ca {total} tran FINISHED -> Chot matches_full.parquet")
                    target_matches.coalesce(1).write.mode("overwrite").parquet(str(matches_full_file))

        # Thuc hien Delete -> Append dung 1 noi duy nhat neu co target_matches
        if target_matches is not None:
            referee_files = [str(f) for f in season_dir.glob("matches__referees_*.parquet")]
            dedup_referees = None
            if referee_files:
                raw_referees = spark.read.parquet(*referee_files)
                dedup_referees = raw_referees.join(
                    target_matches.select("_dlt_id"),
                    raw_referees._dlt_parent_id == target_matches._dlt_id,
                    "inner"
                ).select(raw_referees["*"]).dropDuplicates(["id", "_dlt_parent_id"])

            # Delete -> Append cho matches va referees
            execute_jdbc_sql(spark, f"DELETE FROM raw_matches_referees WHERE _dlt_parent_id IN (SELECT _dlt_id FROM raw_matches WHERE season = {season})")
            execute_jdbc_sql(spark, f"DELETE FROM raw_matches WHERE season = {season}")

            write_to_postgres(target_matches, "raw_matches", mode="append")
            if dedup_referees:
                write_to_postgres(dedup_referees, "raw_matches_referees", mode="append")

        # 2. Teams
        team_files = [str(f) for f in season_dir.glob("teams_*.parquet") if "squad" not in f.name]
        dedup_season_teams = None
        if team_files:
            print(f"Season {season}: Process teams...")
            raw_season_teams = spark.read.parquet(*team_files)
            team_window = Window.partitionBy("id").orderBy(col("last_updated").desc_nulls_last(), col("_dlt_load_id").desc_nulls_last())
            dedup_season_teams = raw_season_teams.withColumn("rn", row_number().over(team_window)).filter(col("rn") == 1).drop("rn").withColumn("season", lit(season))

            execute_jdbc_sql(spark, f"DELETE FROM raw_teams WHERE season = {season}")
            write_to_postgres(dedup_season_teams, "raw_teams", mode="append")

        # 3. Squad
        squad_files = [str(f) for f in season_dir.glob("teams__squad_*.parquet")]
        if squad_files and dedup_season_teams:
            print(f"Season {season}: Process squad...")
            raw_squad = spark.read.parquet(*squad_files)
            season_squad = raw_squad.join(
                dedup_season_teams.select(col("_dlt_id").alias("parent_id_key"), col("id").alias("team_id")),
                raw_squad._dlt_parent_id == col("parent_id_key"),
                "inner"
            ).drop("parent_id_key").withColumn("season", lit(season))

            execute_jdbc_sql(spark, f"DELETE FROM raw_teams_squad WHERE season = {season}")
            write_to_postgres(season_squad, "raw_teams_squad", mode="append")

    print("Finished Load")

def main():
    spark = get_spark_session()
    spark.sparkContext.setLogLevel("WARN")
    process_pipeline(spark)

if __name__ == "__main__":
    main()