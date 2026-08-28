with source as (
    select * from {{ source('epl_postgres', 'raw_teams') }}
),

dedup_source as (
    select *,
        row_number() over (
            partition by id, season 
            order by last_updated desc nulls last, _dlt_load_id desc nulls last
        ) as rn
    from source
),

renamed as (
    select
        cast(id as integer) as team_id,
        cast(season as integer) as season,
        cast(name as varchar) as team_name,
        cast(short_name as varchar) as short_name,
        cast(tla as varchar) as tla,
        cast(crest as varchar) as crest,
        cast(address as varchar) as address,
        cast(website as varchar) as website,
        cast(founded as integer) as founded_year,
        cast(club_colors as varchar) as club_colors,
        cast(venue as varchar) as venue,
        cast(last_updated as timestamp) as last_updated,
        cast(_dlt_load_id as varchar) as _dlt_load_id,
        cast(_dlt_id as varchar) as _dlt_id
    from dedup_source
    where rn = 1
)

select * from renamed
