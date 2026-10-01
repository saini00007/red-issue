select 'oob_totals', count(*), count(*) filter (where fired_at is not null) fired, count(*) filter (where fired_at is null) minted_unfired from tenant_xbow.oob_token;
select 'oob_per_scan', count(*) filter (where fired_at is not null) fired, count(*) filter (where fired_at is null) unfired, count(*) total from tenant_xbow.oob_token group by scan_id order by 3 desc limit 12;
select 'oob_scans_with_tokens', count(distinct scan_id) from tenant_xbow.oob_token;
select 'oob_cell_link', count(*) filter (where cell_id is not null) with_cell, count(*) filter (where cell_id is null) no_cell from tenant_xbow.oob_token;
select 'oob_vs_confirmed', (select count(*) from tenant_xbow.ledger_cell where state='confirmed') confirmed_cells, (select count(*) from tenant_xbow.oob_token where fired_at is not null) fired_tokens;
