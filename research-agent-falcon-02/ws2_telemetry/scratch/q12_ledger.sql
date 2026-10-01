select 'LEDGER_TOTAL', count(*)::text from tenant_xbow.ledger_cell;
select 'LEDGER_BY_STATE', state, count(*)::text from tenant_xbow.ledger_cell group by state order by 3 desc;
select 'LEDGER_BY_APPLICABLE', applicable::text, count(*)::text from tenant_xbow.ledger_cell group by applicable;
select 'LEDGER_CLAIMED_BY_FLOOR', case when claimed_by like 'floor-%' then 'floor-*' when claimed_by is null then 'null' else 'other' end, count(*)::text
  from tenant_xbow.ledger_cell group by 1 order by 2 desc;
select 'LEDGER_CLAIM_PREFIX', split_part(claimed_by,'-',1) as pfx, count(*)::text
  from tenant_xbow.ledger_cell where claimed_by is not null group by 1 order by 2 desc limit 20;
select 'LEDGER_STILL_CLAIMED_LEASE_FUTURE', case when lease_expires_at > now() then 'lease_active' else 'lease_expired_or_null' end, count(*)::text
  from tenant_xbow.ledger_cell where claimed_by is not null group by 1;
select 'LEDGER_ATTEMPTS', attempts, count(*)::text from tenant_xbow.ledger_cell group by attempts order by attempts;
select 'LEDGER_BY_SCAN_TOP', scan_id::text, count(*)::text from tenant_xbow.ledger_cell group by 1 order by 2 desc limit 12;
select 'AUDIT_ACTIONS', action, count(*)::text from tenant_xbow.audit_log group by action order by 2 desc limit 40;
select 'AUDIT_TOTAL', count(*)::text from tenant_xbow.audit_log;
