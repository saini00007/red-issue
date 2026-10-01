-- Q4: tool x status by phase via time-window join to scan_phases
select coalesce(p.phase_name,'<no_phase_window>') phase, i.tool_name, i.status, count(*)
from tenant_xbow.tool_invocations i
left join tenant_xbow.scan_phases p
  on p.scan_id=i.scan_id and p.phase_name in ('reconnaissance','exploitation','finalize')
 and i.started_at >= p.started_at and i.started_at < coalesce(p.completed_at, i.started_at + interval '1 second')
group by 1,2,3
having count(*) >= 20
order by 1, 4 desc;