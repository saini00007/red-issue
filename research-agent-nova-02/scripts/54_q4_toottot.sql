select 'status_total', status, count(*) from tenant_xbow.tool_invocations group by 2;
select 'phase_null', count(*) from tenant_xbow.tool_invocations where phase_id is null;