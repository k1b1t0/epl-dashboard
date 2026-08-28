with source as (
    select * from {{ source('epl_postgres', 'raw_teams_squad') }}
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
    from source
    where rn = 1
)

select * from renamed
