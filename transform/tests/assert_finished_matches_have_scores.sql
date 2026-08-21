-- Singular Test: Kiem tra tat ca cac tran dau da FINISHED thi bat buoc phai co ti so (khong duoc NULL)
-- Quy tac cua Singular Test: Tra ve cac dong VI PHAM (neu tra ve 0 dong -> PASS)

select
    match_id,
    season,
    matchday,
    match_status,
    full_time_home_score,
    full_time_away_score
from {{ ref('stg_matches') }}
where match_status = 'FINISHED'
  and (full_time_home_score is null or full_time_away_score is null)
