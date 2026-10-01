\pset pager off
\timing off
-- Q1: scan inventory (duration, cap, phase, status)
select scan_id, status, mode, time_cap_seconds,
       to_char(started_at,'MM-DD HH24:MI') as started,
       to_char(completed_at,'MM-DD HH24:MI') as done,
       round(extract(epoch from (coalesce(completed_at, now())-started_at))/60,1) as dur_min,
       current_phase, left(coalesce(failure_reason,''),40) as fail
from tenant_xbow.scans order by created_at desc limit 25;