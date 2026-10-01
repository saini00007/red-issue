\echo ===tool_name-distribution===
select tool_name, count(*) from tenant_xbow.tool_invocations group by 1 order by 2 desc;
\echo ===newtech-tools-ever-fired===
select tool_name, count(*) from tenant_xbow.tool_invocations
where tool_name ~* 'graphql|chain|channel|ws|oob|dom|instrument|playwright' group by 1 order by 2 desc;
\echo ===floor-tools-ever-fired===
select tool_name, count(*) from tenant_xbow.tool_invocations where tool_name like 'exploit_floor%' group by 1 order by 2 desc;
\echo ===evidence-object-kinds===
select kind, count(*) from tenant_xbow.evidence_object group by 1 order by 2 desc;
