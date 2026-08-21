with finished_matches as (
    select * 
    from {{ ref('int_team_matches') }}
    where match_status = 'FINISHED'
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
    from aggregated
)

select * from ranked
order by season desc, rank asc
