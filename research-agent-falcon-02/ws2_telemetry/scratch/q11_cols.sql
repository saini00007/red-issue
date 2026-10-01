select table_name, column_name, data_type
from information_schema.columns
where table_schema='tenant_xbow'
  and table_name in ('ledger_cell','audit_log','coverage_ledger','worker_runs','agent_messages','oob_token','scan_events','tool_invocations')
order by table_name, ordinal_position;
