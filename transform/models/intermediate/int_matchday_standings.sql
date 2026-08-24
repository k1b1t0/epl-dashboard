with finished_matches as (
    select * 
    from {{ ref('int_team_matches') }}
    where match_status = 'FINISHED'
),

-- Tong hop chi so theo tung vong dau (matchday) va doi bong
matchday_summary as (
    select
        team_id,
        season,
        matchday,
        count(match_id) as md_played,
        count(case when result = 'WIN' then 1 end) as md_win,
        count(case when result = 'LOST' then 1 end) as md_lose,
        count(case when result = 'DRAW' then 1 end) as md_draw,
        sum(goals_for) as md_goals_for,
        sum(goals_against) as md_goals_against,
        sum(points_earned) as md_points
    from finished_matches
    group by season, matchday, team_id
),

-- Tinh tong don luy ke qua cac vong dau bang Window Function
cumulative_standings as (
    select
        team_id,
        season,
        matchday,
        sum(md_played) over (
            partition by season, team_id 
            order by matchday 
            rows between unbounded preceding and current row
        ) as played,

        sum(md_win) over (
            partition by season, team_id 
            order by matchday 
            rows between unbounded preceding and current row
        ) as win,

        sum(md_lose) over (
            partition by season, team_id 
            order by matchday 
            rows between unbounded preceding and current row
        ) as lose,

        sum(md_draw) over (
            partition by season, team_id 
            order by matchday 
            rows between unbounded preceding and current row
        ) as draw,

        sum(md_goals_for) over (
            partition by season, team_id 
            order by matchday 
            rows between unbounded preceding and current row
        ) as goals_scored,

        sum(md_goals_against) over (
            partition by season, team_id 
            order by matchday 
            rows between unbounded preceding and current row
        ) as goals_conceded,

        (
            sum(md_goals_for) over (
                partition by season, team_id 
                order by matchday 
                rows between unbounded preceding and current row
            )
            - 
            sum(md_goals_against) over (
                partition by season, team_id 
                order by matchday 
                rows between unbounded preceding and current row
            )
        ) as goals_difference,

        sum(md_points) over (
            partition by season, team_id 
            order by matchday 
            rows between unbounded preceding and current row
        ) as points
    from matchday_summary
),

-- Xep hang theo tung vong dau
ranked_standings as (
    select
        team_id,
        season,
        matchday,
        played,
        win,
        lose,
        draw,
        goals_scored,
        goals_conceded,
        goals_difference,
        points,
        rank() over (
            partition by season, matchday 
            order by 
                points desc, 
                goals_difference desc, 
                goals_scored desc
        ) as rank
    from cumulative_standings
)

select * from ranked_standings
order by season desc, matchday asc, rank asc