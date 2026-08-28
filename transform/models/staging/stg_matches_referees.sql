with source as (
    select * from {{ source('epl_postgres', 'raw_matches_referees') }}
),

renamed as (
    select
        cast(id as integer) as referee_id,
        cast(name as varchar) as referee_name,
        cast(type as varchar) as referee_type,
        cast(nationality as varchar) as nationality,
        cast(_dlt_parent_id as varchar) as match_dlt_id,
        cast(_dlt_list_idx as integer) as _dlt_list_idx,
        cast(_dlt_id as varchar) as _dlt_id
    from source
)

select * from renamed
