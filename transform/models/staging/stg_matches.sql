with source as (
    select * from {{ source('epl_postgres', 'raw_matches') }}
),

dedup_source as (
    select *,
        row_number() over (
            partition by id 
            order by last_updated desc nulls last, _dlt_load_id desc nulls last
        ) as rn
    from source
),

renamed as (
    select
        -- Match Info
        cast(id as integer) as match_id,
        cast(season as integer) as season,
        cast(matchday as integer) as matchday,
        cast(status as varchar) as match_status,
        cast(stage as varchar) as stage,
        cast("group" as varchar) as match_group,
        cast(utc_date as timestamp) as utc_date,
        cast(last_updated as timestamp) as last_updated,
        
        -- Home Team
        cast(home_team__id as integer) as home_team_id,
        cast(home_team__name as varchar) as home_team_name,
        cast(home_team__short_name as varchar) as home_team_short_name,
        cast(home_team__tla as varchar) as home_team_tla,
        cast(home_team__crest as varchar) as home_team_crest,
        
        -- Away Team
        cast(away_team__id as integer) as away_team_id,
        cast(away_team__name as varchar) as away_team_name,
        cast(away_team__short_name as varchar) as away_team_short_name,
        cast(away_team__tla as varchar) as away_team_tla,
        cast(away_team__crest as varchar) as away_team_crest,
        
        -- Score
        cast(score__winner as varchar) as winner,
        cast(score__duration as varchar) as duration,
        cast(score__full_time__home as integer) as full_time_home_score,
        cast(score__full_time__away as integer) as full_time_away_score,
        cast(score__half_time__home as integer) as half_time_home_score,
        cast(score__half_time__away as integer) as half_time_away_score,
        
        -- Metadata & dlt IDs
        cast(competition__id as integer) as competition_id,
        cast(competition__name as varchar) as competition_name,
        cast(competition__code as varchar) as competition_code,
        cast(_dlt_id as varchar) as _dlt_id,
        cast(_dlt_load_id as varchar) as _dlt_load_id

    from dedup_source
    where rn = 1
)

select * from renamed
