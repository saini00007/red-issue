\pset pager off
with s as (
  select scan_id, status,
         round(extract(epoch from (coalesce(completed_at,now())-started_at))/60,1) scan_min
  from tenant_xbow.scans where started_at > now() - interval '4 days'
)
select left(s.scan_id::text,8) sid, s.status, s.scan_min,
       count(w.id) workers,
       count(*) filter (where w.finished_at is null) open_w,
       round(avg(extract(epoch from (w.finished_at-w.started_at))) filter (where w.finished_at is not null)) avg_s,
       round(max(extract(epoch from (w.finished_at-w.started_at))) filter (where w.finished_at is not null)) mx_s,
       count(*) filter (where w.status='ok') ok,
       count(*) filter (where w.status='partial') partial,
       count(*) filter (where w.status='error') err,
       sum(coalesce(w.findings_count,0)) finds, sum(coalesce(w.resolved_count,0)) resv
from s left join tenant_xbow.worker_runs w on w.scan_id=s.scan_id
group by 1,2,3 order by s.scan_min desc;