select 'WORKER_RUNS_TOTAL', count(*)::text from tenant_xbow.worker_runs;
select 'WR_BY_STATUS', status, count(*)::text from tenant_xbow.worker_runs group by status order by 2 desc;
select 'WR_BY_MODEL', coalesce(model_id,'?'), coalesce(provider,'?'), count(*)::text from tenant_xbow.worker_runs group by 2,3 order by 4 desc limit 15;
select 'WR_ERROR_CLASS', k, count(*)::text from (
  select case
    when error is null or error='' then 'none'
    when error ilike '%429%' or error ilike '%rate%limit%' then 'rate_limit_429'
    when error ilike '%no choices%' or error ilike '%empty%' then 'empty_response'
    when error ilike '%context%length%' or error ilike '%too long%' or error ilike '%max_tokens%' then 'context_length'
    when error ilike '%timeout%' or error ilike '%timed out%' then 'timeout'
    when error ilike '%401%' or error ilike '%unauthor%' or error ilike '%key%' then 'auth'
    when error ilike '%500%' or error ilike '%502%' or error ilike '%503%' or error ilike '%504%' then 'upstream_5xx'
    when error ilike '%connection%' or error ilike '%connect%' or error ilike '%reset%' then 'connection'
    else 'other' end as k
  from tenant_xbow.worker_runs) t group by 1 order by 2 desc;
select 'WR_ERROR_OTHER_SAMPLES', left(error,110), count(*)::text from tenant_xbow.worker_runs
  where error is not null and error not like '%429%' and error not like '%choices%'
  group by 2 order by 3 desc limit 20;
select 'AGENT_MESSAGES_TOTAL', count(*)::text from tenant_xbow.agent_messages;
select 'AM_BY_ROLE', role, count(*)::text from tenant_xbow.agent_messages group by role order by 2 desc;
select 'AM_DISTINCT_SCANS', count(distinct scan_id)::text from tenant_xbow.agent_messages;
select 'AM_DISTINCT_AGENTS', count(distinct agent_id)::text from tenant_xbow.agent_messages;
select 'AM_TURN_INDEX', turn_index, count(*)::text from tenant_xbow.agent_messages group by turn_index order by turn_index nulls last limit 25;
