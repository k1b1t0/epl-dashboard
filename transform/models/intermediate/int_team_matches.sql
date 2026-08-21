with home_team_matches as (
    select
        concat(match_id, '_', home_team_id) as team_match_id,
        match_id,
        season,
        matchday,
        utc_date,
        match_status,
        home_team_id as team_id,
        away_team_id as opponent_id,
        cast(1 as boolean) as is_home,
        full_time_home_score as goals_for,
        full_time_away_score as goals_against,
        {{ get_match_result('full_time_home_score', 'full_time_away_score') }} as result,
        {{ get_points_earned('full_time_home_score', 'full_time_away_score') }} as points_earned
    from {{ ref('stg_matches') }}
),

away_team_matches as (
    select
        concat(match_id, '_', away_team_id) as team_match_id,
        match_id,
        season,
        matchday,
        utc_date,
        match_status,
        away_team_id as team_id,
        home_team_id as opponent_id,
        cast(0 as boolean) as is_home,
        full_time_away_score as goals_for,
        full_time_home_score as goals_against,
        {{ get_match_result('full_time_away_score', 'full_time_home_score') }} as result,
        {{ get_points_earned('full_time_away_score', 'full_time_home_score') }} as points_earned
    from {{ ref('stg_matches') }}
)

select * from home_team_matches
union all
select * from away_team_matches
