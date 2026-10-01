select column_name, data_type from information_schema.columns where table_schema='tenant_xbow' and table_name='scan_phases' order by ordinal_position;
select 'dur_check', count(*), count(*) filter (where finished_at is null) null_fin, round(min(extract(epoch from (finished_at-started_at)))::numeric,3), round(max(extract(epoch from (finished_at-started_at)))::numeric,3), count(*) filter (where finished_at>started_at) positive from tenant_xbow.tool_invocations;
select 'tool_status', tool_name, status, count(*) from tenant_xbow.tool_invocations group by 2,3 order by 2,4 desc;
