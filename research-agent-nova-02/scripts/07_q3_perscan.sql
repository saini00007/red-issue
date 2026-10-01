select s.scan_id, s.status,
  count(*) total,
  count(*) filter (where c.applicable) applicable,
  count(*) filter (where c.applicable and c.state in ('confirmed','tested_clean','blocked')) resolved,
  count(*) filter (where c.applicable and c.state='attempted') attempted,
  count(*) filter (where c.applicable and c.state in ('untested','testing')) open_cells,
  case when count(*) filter (where c.applicable)>0
       then round(100.0*count(*) filter (where c.applicable and c.state in ('confirmed','tested_clean','blocked'))/count(*) filter (where c.applicable),1) end
from tenant_xbow.scans s join tenant_xbow.ledger_cell c on c.scan_id=s.scan_id
group by 1,2 order by 4 desc limit 14;
