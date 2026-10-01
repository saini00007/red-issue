\pset pager off
-- Q2 PROOF: run the EXACT release_cells WHERE-clause as a SELECT (read-only), per claimed_by
select claimed_by,
  count(*) as rows_release_cells_would_match
from tenant_xbow.ledger_cell
where scan_id='84aea81a-7e43-495c-9974-ca064ddd3552'::uuid
  and claimed_by is not null and state in ('untested','testing')
group by 1 order by 2 desc;
-- do any worker_runs.worker_id values ever appear as ledger_cell.claimed_by? (all-time)
select count(*) as worker_ids_that_ever_owned_a_cell
from (select distinct worker_id from tenant_xbow.worker_runs) w
where exists (select 1 from tenant_xbow.ledger_cell c where c.claimed_by = w.worker_id);
-- do any worker_runs rows match a batch/escalation naming convention?
select count(*) filter (where worker_id like 'batch%') batch_named,
       count(*) filter (where worker_id like 'esc%') esc_named,
       count(*) filter (where worker_id like 'wave%') wave_named,
       count(*) filter (where worker_id like 'floor%') floor_named,
       count(*) total
from tenant_xbow.worker_runs;