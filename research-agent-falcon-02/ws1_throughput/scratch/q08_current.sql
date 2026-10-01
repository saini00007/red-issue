\pset pager off
-- current scan claimed_by breakdown
select claimed_by, state, count(*) cells,
       count(*) filter (where lease_expires_at < now()) lease_exp,
       round(extract(epoch from (max(lease_expires_at)-min(updated_at)))/60) span_min
from tenant_xbow.ledger_cell
where scan_id='84aea81a-7e43-495c-9974-ca064ddd3552'::uuid and claimed_by is not null
group by 1,2 order by 3 desc limit 30;
-- attempts histogram for current scan
select attempts, state, count(*) from tenant_xbow.ledger_cell
where scan_id='84aea81a-7e43-495c-9974-ca064ddd3552'::uuid and applicable=true
group by 1,2 order by 1,2;