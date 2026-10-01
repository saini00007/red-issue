\pset pager off
-- worker duration histogram for live scan
select worker_id, status, round(extract(epoch from (coalesce(finished_at,now())-started_at))) dur_s,
       findings_count, left(coalesce(error,''),70) err
from tenant_xbow.worker_runs where scan_id='84aea81a-7e43-495c-9974-ca064ddd3552'::uuid
order by started_at;
-- global: how many workers ended via wall/stuck/preempt across all scans
select left(coalesce(error,''),60) err, count(*), round(avg(extract(epoch from (finished_at-started_at)))) avg_s
from tenant_xbow.worker_runs where finished_at is not null
group by 1 order by 2 desc limit 25;