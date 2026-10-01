\pset pager off
-- Q5e: na_reason for terminal 'attempted' cells (reason_code proxy)
select coalesce(nullif(na_reason,''),'(empty)') reason, count(*) cells,
       count(*) filter (where attempts=0) zero_attempt
from tenant_xbow.ledger_cell where applicable=true and state='attempted'
group by 1 order by 2 desc limit 20;
-- Q5f: per-scan terminal state for the long scans
select left(scan_id::text,8) sid, count(*) applicable,
  count(*) filter (where state='attempted') attempted,
  count(*) filter (where state='untested') untested,
  count(*) filter (where state='testing') testing,
  count(*) filter (where state='tested_clean') clean,
  count(*) filter (where state='confirmed') confirmed,
  count(*) filter (where state='blocked') blocked
from tenant_xbow.ledger_cell where applicable=true
group by 1 having count(*)>0 order by 2 desc limit 15;