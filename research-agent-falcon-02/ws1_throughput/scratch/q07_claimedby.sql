\pset pager off
-- Q2a: what claimed_by values actually exist on ledger_cell (applicable, open only)
select claimed_by, count(*) cells, count(distinct scan_id) scans,
       count(*) filter (where lease_expires_at is not null and lease_expires_at < now()) lease_expired,
       count(*) filter (where state='testing') testing
from tenant_xbow.ledger_cell
where applicable=true and state in ('untested','testing') and claimed_by is not null
group by 1 order by 2 desc limit 40;