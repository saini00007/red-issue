select 'CLAIM_BY_FLOOR', case when claimed_by like 'floor-%' then 'floor-*' when claimed_by is null then 'null' else 'other' end as k, count(*)::text as n
  from tenant_xbow.ledger_cell group by 2;
select 'CLAIM_PREFIX', split_part(claimed_by,'-',1) as pfx, count(*)::text as n
  from tenant_xbow.ledger_cell where claimed_by is not null group by 2 order by 3 desc;
select 'TESTING_STATE_CLAIMEDBY', case when claimed_by is null then 'null' when claimed_by like 'floor-%' then 'floor-*' else 'other' end, count(*)::text
  from tenant_xbow.ledger_cell where state='testing' group by 2;
select 'LEASE_STATE', case when claimed_by is null then 'no_claim' when lease_expires_at is null then 'claim_no_lease' when lease_expires_at > now() then 'lease_active' else 'lease_expired' end, count(*)::text
  from tenant_xbow.ledger_cell group by 2;
select 'LEASETIME_BUCKET', case when claimed_by is null then 'no_claim' else least(10, floor(extract(epoch from (lease_expires_at - updated_at))/600)::int)::text end, count(*)::text
  from tenant_xbow.ledger_cell group by 2 order by 2;
select 'DISTINCT_SCANS_IN_LEDGER', count(distinct scan_id)::text from tenant_xbow.ledger_cell;
select 'CELLS_PER_SCAN_DISTINCT', cnt::text, count(*)::text from (
  select scan_id, count(*) cnt from tenant_xbow.ledger_cell group by 1) t group by 1 order by 1::int desc limit 15;
select 'FLOOR_PREFIX_CLAIMED_BY_SCAN', scan_id::text, count(*)::text
  from tenant_xbow.ledger_cell where claimed_by like 'floor-%' group by 1 order by 2 desc limit 10;
select 'METHODS_FLOOR_CELLS', count(*)::text from tenant_xbow.ledger_cell
  where methods_used::text like '%exploit_floor%';
