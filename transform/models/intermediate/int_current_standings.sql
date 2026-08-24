with finished_matches as (
    select * 
    from {{ ref('int_team_matches') }}
    where match_status = 'FINISHED'
),

team_season as (
    select team_id, season
    from {{ ref('stg_teams') }}
),

aggregated as (
    select
        team_id,
        season,
        count(match_id) as played,
        count(case when result = 'WIN' then 1 end) as win,
        count(case when result = 'LOST' then 1 end) as lose,
        count(case when result = 'DRAW' then 1 end) as draw,
        sum(goals_for) as goals_scored,
        sum(goals_against) as goals_conceded,
        sum(goals_for) - sum(goals_against) as goals_difference,
        sum(points_earned) as points
    from finished_matches
    group by season, team_id
),

add_null_teams as (
    select
        ts.team_id,
        ts.season,
        coalesce(a.played, 0) as played,
        coalesce(a.win, 0) as win,
        coalesce(a.lose, 0) as lose,
        coalesce(a.draw, 0) as draw,
        coalesce(a.goals_scored, 0) as goals_scored,
        coalesce(a.goals_conceded, 0) as goals_conceded,
        coalesce(a.goals_difference, 0) as goals_difference,
        coalesce(a.points, 0) as points
    from team_season ts
    left join aggregated a
        on ts.team_id = a.team_id 
       and ts.season = a.season
),

ranked as (
    select
        team_id,
        season,
        played,
        win,
        lose,
        draw,
        goals_scored,
        goals_conceded,
        goals_difference,
        points,
        dense_rank() over (
            partition by season 
            order by 
                points desc, 
                goals_difference desc, 
                goals_scored desc
        ) as rank
    from add_null_teams
)

select * from ranked
order by season desc, rank asc
