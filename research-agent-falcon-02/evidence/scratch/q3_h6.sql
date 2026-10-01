\echo ===H6-attempt-distribution-all-scans===
select attempts, count(*) as cells from tenant_xbow.ledger_cell group by attempts order by attempts;
\echo ===H6-total-cells-vs-sum-attempts===
select count(*) as cells, sum(attempts) as attempt_sum, round(avg(attempts),2) as avg_attempts,
       count(*) filter (where attempts>1) as cells_retried,
       round(100.0*count(*) filter (where attempts>1)/count(*),1) as pct_retried
from tenant_xbow.ledger_cell;
\echo ===H6-top10-scans-by-attempts===
select c.scan_id::text, count(*) as cells, sum(c.attempts) as attempts,
       round(avg(c.attempts),2) as avg_att,
       count(*) filter (where c.attempts>1) as retried,
       (select count(*) from tenant_xbow.worker_runs w where w.scan_id=c.scan_id) as worker_runs,
       (select count(*) from tenant_xbow.findings f where f.scan_id=c.scan_id) as findings
from tenant_xbow.ledger_cell c group by c.scan_id order by attempts desc limit 10;
\echo ===H6-leases-left-held===
select state, count(*) as cells, count(*) filter (where claimed_by is not null) as still_claimed,
       count(*) filter (where lease_expires_at is not null and lease_expires_at > now()) as lease_live,
       count(*) filter (where lease_expires_at is not null and lease_expires_at <= now()) as lease_expired
from tenant_xbow.ledger_cell group by state order by cells desc;
\echo ===H6-worker-runs-status===
select status, count(*) from tenant_xbow.worker_runs group by status order by 2 desc;
\echo ===H6-worker_runs-resolved-vs-attempts(top scans)===
select w.scan_id::text, count(*) as runs, sum(w.resolved_count) as resolved_sum,
       sum(w.findings_count) as findings_sum
from tenant_xbow.worker_runs w group by w.scan_id order by resolved_sum desc nulls last limit 8;
