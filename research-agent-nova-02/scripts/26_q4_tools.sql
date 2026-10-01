select 'tool_phase_status', coalesce(p.phase_name,'<none>'), i.status, count(*) from tenant_xbow.tool_invocations i left join tenant_xbow.scan_phases p on p.phase_id=i.phase_id group by 2,3 order by 2,4 desc;
select 'tool_phase_dur', coalesce(p.phase_name,'<none>'), count(*), round(avg(extract(epoch from (i.finished_at-i.started_at)))::numeric,1) s, round(sum(extract(epoch from (i.finished_at-i.started_at)))::numeric,0) tot_s
from tenant_xbow.tool_invocations i left join tenant_xbow.scan_phases p on p.phase_id=i.phase_id where i.finished_at is not null group by 2 order by 5 desc;
select 'inv_status_total', status, count(*) from tenant_xbow.tool_invocations group by 2 order by 2 desc;
