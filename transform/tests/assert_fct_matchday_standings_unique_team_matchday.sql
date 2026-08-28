-- Kiem tra moi doi bong trong mot mua giai chi co 1 vi tri duy nhat tai moi vong dau
select
    season,
    team_id,
    matchday,
    count(*) as duplicate_count
from {{ ref('fct_matchday_standings') }}
group by season, team_id, matchday
having count(*) > 1
