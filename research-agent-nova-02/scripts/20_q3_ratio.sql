select round(avg(r),3)::text, sum(res)::text, sum(ap)::text,
  round(100.0*sum(res)/sum(ap),1)::text
from (select count(*) filter (where c.applicable and c.state in ('confirmed','tested_clean','blocked')) res,
             count(*) filter (where c.applicable) ap,
             count(*) filter (where c.applicable and c.state in ('confirmed','tested_clean','blocked'))::numeric / nullif(count(*) filter (where c.applicable),0) r
      from tenant_xbow.ledger_cell c group by c.scan_id) t;
select count(*) from (select count(*) filter (where c.applicable and c.state in ('confirmed','tested_clean','blocked')) res
      from tenant_xbow.ledger_cell c group by c.scan_id) t where res=0;
