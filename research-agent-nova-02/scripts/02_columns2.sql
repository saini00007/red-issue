select table_name||' | '||column_name||' | '||data_type
from information_schema.columns
where table_schema='tenant_xbow' and table_name in ('evidence_object','chain_node','chain_edge','coverage_ledger','scan_events','scan_phases','worker_runs','tool_invocations','inventory_element')
order by table_name, ordinal_position;
