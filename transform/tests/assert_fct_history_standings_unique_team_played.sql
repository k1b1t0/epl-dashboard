-- Kiem tra moi doi bong trong mot mua giai chi co 1 vi tri duy nhat sau tran thu N da thi dau
select
    season,
    team_id,
    played,
    count(*) as duplicate_count
from {{ ref('fct_history_standings') }}
group by season, team_id, played
having count(*) > 1
