\echo ===H6-claimed-by-worker-prefix-distribution===
select split_part(claimed_by,'-',1) as who, count(*) as cells,
       count(*) filter (where lease_expires_at < now()) as expired,
       count(*) filter (where lease_expires_at >= now()) as live
from tenant_xbow.ledger_cell where claimed_by is not null group by 1 order by 2 desc;
\echo ===H6-floor-claims-never-released===
select claimed_by, state, count(*), min(attempts), max(attempts)
from tenant_xbow.ledger_cell
where claimed_by like 'floor-%' group by 1,2 order by 3 desc;
\echo ===H6-wave-claims===
select left(claimed_by, 12) as w, count(*) from tenant_xbow.ledger_cell
where claimed_by like 'wave%' group by 1 order by 2 desc limit 15;
\echo ===H6-distinct-workers-that-touched-attempted-cells===
select count(distinct claimed_by) from tenant_xbow.ledger_cell where claimed_by is not null;
