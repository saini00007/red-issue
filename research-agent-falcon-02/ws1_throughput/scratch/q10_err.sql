\pset pager off
-- status distribution all-time
select status, count(*), round(avg(extract(epoch from (coalesce(finished_at,now())-started_at)))) avg_s
from tenant_xbow.worker_runs group by 1 order by 2 desc;
-- which scans hit the 0s wall, and when
select left(scan_id::text,8) sid, to_char(min(started_at),'MM-DD HH24:MI') first_w,
       count(*) filter (where error like '%backstop 0s%') wall0,
       count(*) filter (where error like '%wall cap 0s%') cap0,
       count(*) filter (where error like '%no choices%') nochoices,
       count(*) total
from tenant_xbow.worker_runs group by 1
having count(*) filter (where error like '%0s%')>0 or count(*) filter (where error like '%no choices%')>3
order by 5 desc limit 20;
-- findings vs worker productivity per scan (last 8 scans)
select left(w.scan_id::text,8) sid, count(*) workers,
  count(*) filter (where w.status='ok') ok,
  count(*) filter (where coalesce(w.findings_count,0)>0) prod,
  round(avg(coalesce(w.findings_count,0)),1) avg_f,
  count(distinct w.phase) phases
from tenant_xbow.worker_runs w group by 1 order by max(w.started_at) desc limit 10;