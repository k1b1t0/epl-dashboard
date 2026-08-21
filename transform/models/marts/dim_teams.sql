with teams as (
    select * from {{ ref('stg_teams') }}
),

dedup_teams as (
    select
        team_id,
        season,
        team_name,
        short_name,
        tla,
        crest,
        address,
        website,
        founded_year,
        club_colors,
        venue,
        last_updated,
        row_number() over (
            partition by team_id
            order by season desc, last_updated desc
        ) as rn
    from teams
)

select
    team_id,
    team_name,
    short_name,
    tla,
    crest,
    season,
    address,
    website,
    founded_year,
    club_colors,
    venue
from dedup_teams
where rn = 1