from pyspark.sql import SparkSession
from pyspark.sql.window import Window
from pyspark.sql.functions import col, row_number, lit

from load.config import RAW_DIR, SEASONS, EPL_MATCHES_TOTAL
from load.db import execute_sql, read_from_postgres, write_to_postgres
from load.loader import load_matches_from_raw, upsert_matches, dedup_latest, load_teams_and_squad

def get_spark_session() -> SparkSession:
    return SparkSession.builder \
        .appName("EPL_Parquet_To_Postgres") \
        .config("spark.jars.packages", "org.postgresql:postgresql:42.7.3") \
        .config("spark.sql.shuffle.partitions", "4") \
        .getOrCreate()


def process_pipeline(spark: SparkSession):
    print("Start Load")

    for season in SEASONS:
        season_dir = RAW_DIR / str(season)
        if not season_dir.exists():
            continue
        print(f"Season {season}")

        # Matches
        matches_full_file = season_dir / f"matches_full_{season}.parquet"
        target_matches = None

        if matches_full_file.exists():
            print(f"Season {season} finished")

            # Check neu da ton tai ban ghi trong DWH
            check_matches_existed = read_from_postgres(
                spark, sql=f"(SELECT COUNT(*) FROM raw_matches WHERE season = {season}) as t"
            )
            count_val = check_matches_existed.first()[0]

            if count_val != 0:
                continue
            else:
                target_matches = spark.read.parquet(str(matches_full_file))
        else:
            target_matches = load_matches_from_raw(spark, season_dir)
        upsert_matches(target_matches, season, matches_full_file)

        # Teams & Squads
        load_teams_and_squad(spark, season, season_dir)

    print("Finished Load")

def main():
    spark = get_spark_session()
    spark.sparkContext.setLogLevel("WARN")
    process_pipeline(spark)

if __name__ == "__main__":
    main()