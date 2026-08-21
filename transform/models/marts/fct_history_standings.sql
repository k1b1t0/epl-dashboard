with history_standings as (
    select * from {{ ref('int_history_standings') }}
),

teams as (
    select * from {{ ref('dim_teams') }}
)

select
    s.match_id,
    s.season,
    s.utc_date,
    s.rank,
    s.team_id,
    t.team_name,
    t.short_name,
    t.tla,
    t.crest,
    s.played,
    s.win,
    s.draw,
    s.lose,
    s.goals_scored,
    s.goals_conceded,
    s.goals_difference,
    s.points
from history_standings s
left join teams t on s.team_id = t.team_id
order by s.season desc, s.utc_date asc, s.rank asc
