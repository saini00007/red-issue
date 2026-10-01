select 'oob_token_total', count(*) from tenant_xbow.oob_token;
select 'with_cell_id', count(*) from tenant_xbow.oob_token where cell_id is not null;
select 'with_endpoint', count(*) from tenant_xbow.oob_token where endpoint is not null and endpoint<>'';
select 'unfired', count(*) from tenant_xbow.oob_token where fired_at is null;
select 'per_scan', scan_id, count(*), count(cell_id) from tenant_xbow.oob_token group by 2 order by 3 desc limit 8;