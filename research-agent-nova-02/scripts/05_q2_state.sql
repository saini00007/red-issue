select 'cell_state', state, count(*) from tenant_xbow.ledger_cell group by 2 order by 3 desc;
select 'cell_applicable', applicable::text, count(*) from tenant_xbow.ledger_cell group by 2 order by 3 desc;
select 'cell_state_x_applicable', coalesce(state,'<null>'), applicable::text, count(*) from tenant_xbow.ledger_cell group by 2,3 order by 1,2;
select 'cell_attempts', attempts, count(*) from tenant_xbow.ledger_cell group by 2 order by 2;
select 'cell_with_finding', (finding_id is not null)::text, count(*) from tenant_xbow.ledger_cell group by 2;
select 'cell_with_evidence', (jsonb_array_length(coalesce(evidence_ids,'[]'::jsonb))>0)::text, count(*) from tenant_xbow.ledger_cell group by 2;
select 'cells_per_scan_total', count(*), count(distinct scan_id) from tenant_xbow.ledger_cell;
