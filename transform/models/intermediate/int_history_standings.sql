with finished_matches as (
    select * 
    from {{ ref('int_team_matches') }}
    where match_status = 'FINISHED'
),

match_events as (
    select
        match_id,
        team_id,
        season,
        utc_date,
        1 as m_played,
        case when result = 'WIN' then 1 else 0 end as m_win,
        case when result = 'LOST' then 1 else 0 end as m_lose,
        case when result = 'DRAW' then 1 else 0 end as m_draw,
        goals_for as m_goals_scored,
        goals_against as m_goals_conceded,
        points_earned as m_points
    from finished_matches
),

cumulative_standings as (
    select
        match_id,
        team_id,
        season,
        utc_date,
        
        sum(m_played) over (
            partition by season, team_id
            order by utc_date
            rows between unbounded preceding and current row
        ) as played,

        sum(m_win) over (
            partition by season, team_id
            order by utc_date
            rows between unbounded preceding and current row
        ) as win,

        sum(m_lose) over (
            partition by season, team_id
            order by utc_date
            rows between unbounded preceding and current row
        ) as lose,

        sum(m_draw) over (
            partition by season, team_id
            order by utc_date
            rows between unbounded preceding and current row
        ) as draw,

        sum(m_goals_scored) over (
            partition by season, team_id
            order by utc_date
            rows between unbounded preceding and current row
        ) as goals_scored,

        sum(m_goals_conceded) over (
            partition by season, team_id
            order by utc_date
            rows between unbounded preceding and current row
        ) as goals_conceded,

        (
            sum(m_goals_scored) over (
                partition by season, team_id
                order by utc_date
                rows between unbounded preceding and current row
            )
            -
            sum(m_goals_conceded) over (
                partition by season, team_id
                order by utc_date
                rows between unbounded preceding and current row
            )
        ) as goals_difference,

        sum(m_points) over (
            partition by season, team_id
            order by utc_date
            rows between unbounded preceding and current row
        ) as points
    from match_events
),

ranked_standings as (
    select
        match_id,
        team_id,
        season,
        utc_date,
        played,
        win,
        lose,
        draw,
        goals_scored,
        goals_conceded,
        goals_difference,
        points,
        dense_rank() over (
            partition by season, utc_date
            order by 
                points desc, 
                goals_difference desc, 
                goals_scored desc
        ) as rank
    from cumulative_standings
)

select * from ranked_standings
order by season desc, utc_date asc, rank asc