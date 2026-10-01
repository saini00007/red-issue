\pset pager off
-- Q5: terminal-unresolved ('attempted') by vuln_class, all scans
select vuln_class, count(*) attempted, count(*) filter (where attempts=0) never_claimed
from tenant_xbow.ledger_cell where applicable=true and state='attempted'
group by 1 order by 2 desc limit 15;
-- Q5: scans that reported completed despite >50% of applicable grid attempted
select left(c.scan_id::text,8) sid, s.status,
       count(*) applicable,
       count(*) filter (where c.state='attempted') attempted,
       round(100.0*count(*) filter (where c.state='attempted')/count(*),1) pct_attempted,
       count(*) filter (where c.state in ('tested_clean','confirmed')) actually_resolved
from tenant_xbow.ledger_cell c join tenant_xbow.scans s on s.scan_id=c.scan_id
where c.applicable=true
group by 1,2 having count(*) filter (where c.state='attempted') > count(*)*0.5
order by pct_attempted desc limit 15;