with matchday_standings as (
    select * from {{ ref('int_matchday_standings') }}
),

teams as (
    select * from {{ ref('dim_teams') }}
)

select
    s.season,
    s.matchday,
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
from matchday_standings s
left join teams t on s.team_id = t.team_id
order by s.season desc, s.matchday asc, s.rank asc
