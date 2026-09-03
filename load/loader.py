from pyspark.sql import SparkSession
from pyspark.sql.window import Window
from pyspark.sql.functions import col, row_number, lit

from load.config import EPL_MATCHES_TOTAL
from load.db import upsert_to_postgres

def dedup_latest(target):
    window = Window.partitionBy("id").orderBy(
        col("last_updated").desc_nulls_last(), 
        col("_dlt_load_id").desc_nulls_last()
    )
    return target.withColumn("rn", row_number().over(window)).filter(col("rn")==1).drop("rn")

# Result for target matches
def load_matches_from_raw(spark: SparkSession, season_dir):
    match_files = [str(f) for f in season_dir.glob("matches_[0-9]*.parquet")]
    if not match_files:
        return None
    raw = spark.read.parquet(*match_files)
    return dedup_latest(raw)

def upsert_matches(target_matches, season, matches_full_file):
    # Upsert to Postgres
    if target_matches is None:
        return
    upsert_to_postgres(target_matches, "raw_matches", season)

    # Update full_file
    total = target_matches.count()
    unfinished = target_matches.filter(col("status") != "FINISHED").count()
    if total == EPL_MATCHES_TOTAL and unfinished == 0:
        # Write to 1 .parquet file
        target_matches.toPandas().to_parquet(matches_full_file, index=False)

def load_teams_and_squad(spark, season, season_dir):
    team_files = [str(f) for f in season_dir.glob("teams_*.parquet") if "squad" not in f.name]
    dedup_season_teams = None
    if team_files:
        print(f"Season {season}: Process teams...")
        raw_season_teams = spark.read.parquet(*team_files)
        
        dedup_season_teams = dedup_latest(raw_season_teams).withColumn("season", lit(season))
        upsert_to_postgres(dedup_season_teams, "raw_teams", season)

    squad_files = [str(f) for f in season_dir.glob("teams__squad_*.parquet")]
    if squad_files and dedup_season_teams is not None:
        print(f"Season {season}: Process squad...")
        raw_squad = spark.read.parquet(*squad_files)
        season_squad = raw_squad.join(
            dedup_season_teams.select(col("_dlt_id").alias("parent_id_key"), col("id").alias("team_id")),
            raw_squad._dlt_parent_id == col("parent_id_key"),
            "inner"
        ).drop("parent_id_key").dropDuplicates(["id", "team_id"]).withColumn("season", lit(season))

        upsert_to_postgres(season_squad, "raw_teams_squad", season)
