select s.scan_id, s.status, coalesce(t.ti,0)::text, coalesce(c.total,0)::text, coalesce(c.res,0)::text,
  round(3600.0*coalesce(c.res,0)/nullif(extract(epoch from (s.completed_at-s.created_at)),0),2)::text
from tenant_xbow.scans s
left join (select scan_id, count(*) ti from tenant_xbow.tool_invocations group by 1) t on t.scan_id=s.scan_id
left join (select scan_id, count(*) total, count(*) filter (where state in ('confirmed','tested_clean','blocked')) res
           from tenant_xbow.ledger_cell group by 1) c on c.scan_id=s.scan_id
order by coalesce(t.ti,0) desc limit 15;
select 'tool_inv_status', status, count(*) from tenant_xbow.tool_invocations group by 2 order by 3 desc;
select 'tool_inv_name_top', tool_name, count(*) from tenant_xbow.tool_invocations group by 1 order by 2 desc limit 12;
select 'phases', phase_name, status, count(*) from tenant_xbow.scan_phases group by 1,2 order by 3 desc limit 20;
