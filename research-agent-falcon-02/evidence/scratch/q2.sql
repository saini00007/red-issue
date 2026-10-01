select column_name||' '||data_type from information_schema.columns where table_schema='tenant_xbow' and table_name='ledger_cell' order by ordinal_position;
select '---worker_runs---';
select column_name||' '||data_type from information_schema.columns where table_schema='tenant_xbow' and table_name='worker_runs' order by ordinal_position;
select '---counts---';
select 'scans='||(select count(*) from tenant_xbow.scans)
     ||' ledger_cell='||(select count(*) from tenant_xbow.ledger_cell)
     ||' worker_runs='||(select count(*) from tenant_xbow.worker_runs)
     ||' findings='||(select count(*) from tenant_xbow.findings)
     ||' evidence='||(select count(*) from tenant_xbow.evidence_object)
     ||' tool_invocations='||(select count(*) from tenant_xbow.tool_invocations)
     ||' agent_messages='||(select count(*) from tenant_xbow.agent_messages)
     ||' chain_node='||(select count(*) from tenant_xbow.chain_node);
