-- Q2: interaction timestamps vs scan window
select 'in_window', s.scan_id,
  count(*) interactions,
  count(distinct t.interaction->>'full-id') distinct_ids,
  count(*) filter (where (t.interaction->>'timestamp')::timestamptz >= s.created_at) in_window,
  count(*) filter (where (t.interaction->>'timestamp')::timestamptz < s.created_at) pre_scan,
  min((t.interaction->>'timestamp')::timestamptz) - s.created_at min_offset,
  max((t.interaction->>'timestamp')::timestamptz) - s.created_at max_offset
from tenant_xbow.oob_token t join tenant_xbow.scans s using (scan_id)
group by 2 order by 4 desc;
select 'pre_pct', round(100.0*count(*) filter (where (t.interaction->>'timestamp')::timestamptz < s.created_at)/count(*),1),
  count(*) from tenant_xbow.oob_token t join tenant_xbow.scans s using (scan_id);