select tool_name, count(*) from tenant_xbow.tool_invocations group by tool_name order by 2 desc limit 12;
select phase_name, status, count(*) from tenant_xbow.scan_phases group by phase_name, status order by 3 desc limit 25;
select event_type, count(*) from tenant_xbow.scan_events group by event_type order by 2 desc limit 25;
