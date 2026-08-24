select
    match_id
from {{ ref('stg_matches') }}
where match_status != 'FINISHED'
and (
    full_time_away_score is not null
        or full_time_away_score is not null
        or half_time_home_score is not null
        or half_time_away_score is not null
)