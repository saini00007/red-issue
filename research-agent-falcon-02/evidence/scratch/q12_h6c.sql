\echo ===H6-per-scan-floor-vs-wave-claims-and-attempts===
select c.scan_id::text,
  count(*) filter (where c.claimed_by like 'floor-%') as floor_claimed,
  count(*) filter (where c.claimed_by like 'wave%') as wave_claimed,
  count(*) filter (where c.attempts>1) as retried_cells,
  sum(c.attempts) as attempts_sum,
  (select count(*) from tenant_xbow.worker_runs w where w.scan_id=c.scan_id) as runs,
  (select count(*) from tenant_xbow.tool_invocations t where t.scan_id=c.scan_id) as tool_invocations
from tenant_xbow.ledger_cell c group by c.scan_id
having count(*) filter (where c.attempts>1) > 0 order by retried_cells desc limit 6;
\echo ===H6-total-tool-invocations-vs-resolved-cells===
select (select count(*) from tenant_xbow.tool_invocations) as tool_invocations,
       (select count(*) from tenant_xbow.ledger_cell where state in ('confirmed','tested_clean')) as resolved_cells,
       (select count(*) from tenant_xbow.findings) as db_findings,
       (select count(*) from tenant_xbow.worker_runs) as worker_runs;
\echo ===H6-worker_runs-resolved-sum-total===
select sum(resolved_count) as resolved_sum, sum(findings_count) as findings_claim_sum, count(*) from tenant_xbow.worker_runs;
\echo ===H6-retry-storm-scans-attempts-cap===
select c.scan_id::text, count(*) filter (where c.attempts>=4) as cells_4plus
from tenant_xbow.ledger_cell c group by 1 having count(*) filter (where c.attempts>=4)>0 order by 2 desc limit 6;
