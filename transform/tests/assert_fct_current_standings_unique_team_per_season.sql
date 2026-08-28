-- Kiem tra moi doi bong trong mot mua giai chi co 1 dong duy nhat trong fct_current_standings
select
    season,
    team_id,
    count(*) as duplicate_count
from {{ ref('fct_current_standings') }}
group by season, team_id
having count(*) > 1
