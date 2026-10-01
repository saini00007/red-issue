select 'WR_ERRCLASS', k, count(*)::text from (
  select case
    when coalesce(error,'')='' then 'none'
    when error ilike '%429%' or error ilike '%rate limit%' then 'rate_limit_429'
    when error ilike '%no choices%' or error ilike '%empty%' then 'empty_response'
    when error ilike '%context length%' or error ilike '%too long%' or error ilike '%max_tokens%' then 'context_length'
    when error ilike '%timeout%' or error ilike '%timed out%' then 'timeout'
    when error ilike '%401%' or error ilike '%unauthor%' then 'auth'
    when error ilike '%500%' then 'upstream_500'
    when error ilike '%502%' or error ilike '%bad gateway%' then 'upstream_502'
    when error ilike '%400%' then 'upstream_400'
    when error ilike '%preempted%contract satisfied%' then 'preempted_contract_ok'
    when error ilike '%preempted%' then 'preempted_other'
    when error ilike '%wall cap%' then 'wall_cap'
    when error ilike '%backstop%' then 'backstop'
    else 'other' end as k
  from tenant_xbow.worker_runs) t group by 2 order by 3 desc;
select 'WR_WALLCAP_ZERO', count(*)::text from tenant_xbow.worker_runs where error ilike '%0s exceeded%';
select 'WR_ERR_BY_STATUS', status, k, count(*)::text from (
  select status, case when coalesce(error,'')='' then 'none'
    when error ilike '%429%' or error ilike '%rate limit%' then 'rate_limit_429'
    when error ilike '%no choices%' or error ilike '%empty%' then 'empty_response'
    when error ilike '%context length%' or error ilike '%max_tokens%' then 'context_length'
    when error ilike '%preempted%' then 'preempted'
    when error ilike '%wall%' or error ilike '%backstop%' then 'wall_or_backstop'
    else 'other' end as k
  from tenant_xbow.worker_runs) t group by 2,3 order by 2,4 desc;
select 'WR_SCAN_ERROR_RATE', scan_id::text, count(*)::text, sum(case when status='error' then 1 else 0 end)::text,
       sum(case when status='ok' then 1 else 0 end)::text
  from tenant_xbow.worker_runs group by 1 order by 3::int desc limit 15;
select 'AM_PER_SCAN', scan_id::text, count(*)::text, count(distinct agent_id)::text, max(turn_index)::text
  from tenant_xbow.agent_messages group by 1 order by 2::int desc limit 20;
select 'AM_MODELS', coalesce(model,'?'), count(*)::text from tenant_xbow.agent_messages group by 1 order by 2 desc limit 12;
select 'AM_TOKENS', sum(coalesce(tokens_in,0))::text, sum(coalesce(tokens_out,0))::text, sum(coalesce(cost_usd,0))::text from tenant_xbow.agent_messages;
select 'AM_NULL_TOKENS', count(*) filter (where tokens_in is null)::text, count(*)::text from tenant_xbow.agent_messages;
select 'TOOL_INVOCATIONS', count(*)::text, count(distinct scan_id)::text from tenant_xbow.tool_invocations;
