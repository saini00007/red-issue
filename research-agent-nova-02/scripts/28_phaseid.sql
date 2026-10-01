select 'inv_phase_id', count(*) filter (where phase_id is null) null_phase, count(*) filter (where phase_id is not null) has_phase, count(distinct phase_id) distinct_phase from tenant_xbow.tool_invocations;
select 'scan_phases_cols', count(*) from tenant_xbow.scan_phases;
select 'phase_join', p.phase_name, count(*) from tenant_xbow.tool_invocations i join tenant_xbow.scan_phases p on p.phase_id=i.phase_id group by 1 order by 2 desc;
select 'inv_by_scan_status', i.scan_id, i.status, count(*) from tenant_xbow.tool_invocations i group by 1,2 order by 1 limit 0;
