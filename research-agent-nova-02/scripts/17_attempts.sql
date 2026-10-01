select round(100.0*count(*) filter (where attempts>3)/nullif(count(*),0),2), count(*) filter (where attempts>3), count(*) from tenant_xbow.ledger_cell;
select attempts, state, count(*) from tenant_xbow.ledger_cell where attempts>0 group by 1,2 order by 1,3 desc;
select 'scan_events_per_scan', count(*), count(distinct scan_id), round(avg(n),1), max(n) from (select scan_id, count(*) n from tenant_xbow.scan_events group by 1) t;
select 'tool_inv_per_scan', round(avg(n),1), max(n), min(n) from (select scan_id, count(*) n from tenant_xbow.tool_invocations group by 1) t;
