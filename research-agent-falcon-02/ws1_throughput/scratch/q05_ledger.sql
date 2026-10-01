\pset pager off
-- Q5a: global resolved_count check (is the column ever populated?)
select count(*) total_runs, count(*) filter (where resolved_count is not null) nonnull_resv,
       sum(coalesce(resolved_count,0)) sum_resv, max(resolved_count) max_resv,
       sum(coalesce(findings_count,0)) sum_finds
from tenant_xbow.worker_runs;
-- Q5b: state distribution across ALL scans, applicable only
select state, count(*) cells, count(distinct scan_id) scans
from tenant_xbow.ledger_cell where applicable=true group by 1 order by 2 desc;
-- Q5c: applicable=false excluded counts
select applicable, count(*) from tenant_xbow.ledger_cell group by 1;
-- Q5d: attempts distribution
select attempts, count(*) cells, count(*) filter (where state='attempted') attempted
from tenant_xbow.ledger_cell where applicable=true group by 1 order by 1;