select s.scan_id, s.status,
       count(*) filter (where c.state='attempted')    as attempted,
       count(*) filter (where c.state='tested_clean') as clean,
       count(*) filter (where c.state='confirmed')    as confirmed,
       count(*) filter (where c.state='na')           as na_in_applicable,
       count(*)                                      as applicable
from ledger_cell c join scans s on s.scan_id = c.scan_id
where c.applicable = true
group by s.scan_id, s.status
having count(*) filter (where c.state='attempted') > count(*) * 0.9
order by attempted desc
limit 10;
