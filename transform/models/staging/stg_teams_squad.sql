with source as (
    select * from {{ source('epl_postgres', 'raw_teams_squad') }}
),

dedup_source as (
    select *,
        row_number() over (
            partition by id, team_id, season 
            order by _dlt_load_id desc nulls last
        ) as rn
    from source
),

renamed as (
    select
        cast(id as integer) as player_id,
        cast(team_id as integer) as team_id,
        cast(season as integer) as season,
        cast(name as varchar) as player_name,
        cast(position as varchar) as position,
        cast(date_of_birth as date) as dob,
        cast(nationality as varchar) as nationality,
        cast(_dlt_parent_id as varchar) as team_dlt_id,
        cast(_dlt_list_idx as integer) as _dlt_list_idx,
        cast(_dlt_id as varchar) as _dlt_id
    from dedup_source
    where rn = 1
)

select * from renamed
