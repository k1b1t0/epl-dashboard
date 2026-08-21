with team_matches as (
    select * from {{ ref('int_team_matches') }}
),

teams as (
    select * from {{ ref('dim_teams') }}
)

select
    tm.team_match_id,
    tm.match_id,
    tm.season,
    tm.matchday,
    tm.utc_date,
    tm.match_status,
    tm.is_home,
    
    -- Team details
    tm.team_id,
    t.team_name,
    t.short_name as team_short_name,
    t.tla as team_tla,
    t.crest as team_crest,
    
    -- Opponent details
    tm.opponent_id,
    opp.team_name as opponent_name,
    opp.short_name as opponent_short_name,
    opp.tla as opponent_tla,
    opp.crest as opponent_crest,
    
    -- Scores & Result
    tm.goals_for,
    tm.goals_against,
    tm.result,
    tm.points_earned
from team_matches tm
left join teams t on tm.team_id = t.team_id
left join teams opp on tm.opponent_id = opp.team_id
order by tm.season desc, tm.utc_date desc
