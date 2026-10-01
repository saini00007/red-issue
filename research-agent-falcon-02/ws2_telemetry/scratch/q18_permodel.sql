select 'ERR_EMPTY_BY_MODEL', coalesce(model_id,'?'), count(*)::text,
       round(100.0*count(*) filter (where error ilike '%no choices%' or error ilike '%empty%')/count(*),1)::text
  from tenant_xbow.worker_runs group by 2 order by 3::int desc;
select 'ERR_429_BY_MODEL', coalesce(model_id,'?'), count(*)::text
  from tenant_xbow.worker_runs where error ilike '%429%' or error ilike '%rate limit%' group by 2 order by 3::int desc;
select 'ERR_EMPTY_SAMPLES', left(error,100) as e, count(*)::text
  from tenant_xbow.worker_runs where error ilike '%no choices%' or error ilike '%empty%' group by 2 order by 3::int desc limit 12;
select 'ERR_429_SAMPLES', left(error,100) as e, count(*)::text
  from tenant_xbow.worker_runs where error ilike '%429%' or error ilike '%rate limit%' group by 2 order by 3::int desc limit 8;
select 'ERR_OTHER_SAMPLES', left(error,100) as e, count(*)::text
  from tenant_xbow.worker_runs where coalesce(error,'')<>'' and error not ilike '%429%' and error not ilike '%no choices%'
    and error not ilike '%empty%' and error not ilike '%preempted%' and error not ilike '%wall%' and error not ilike '%backstop%'
  group by 2 order by 3::int desc limit 15;
select 'WR_SCAN_TABLE', s.scan_id::text, count(w.id)::text,
       sum(case when w.status='error' then 1 else 0 end)::text,
       sum(case when w.error ilike '%no choices%' or w.error ilike '%empty%' then 1 else 0 end)::text,
       sum(case when w.error ilike '%429%' or w.error ilike '%rate limit%' then 1 else 0 end)::text,
       s.status
  from tenant_xbow.scans s left join tenant_xbow.worker_runs w on w.scan_id=s.scan_id
  group by 1,7 having count(w.id)>0 order by 3::int desc limit 20;
select 'AM_PER_SCAN', scan_id::text, count(*)::text, count(distinct agent_id)::text, max(turn_index)::text
  from tenant_xbow.agent_messages group by 1 order by 2::int desc limit 20;
select 'AM_MODELS', coalesce(model,'?'), count(*)::text from tenant_xbow.agent_messages group by 1 order by 2 desc limit 12;
select 'SCANS_WITH_ZERO_AGENT_MESSAGES', count(*)::text from tenant_xbow.scans s
  where not exists (select 1 from tenant_xbow.agent_messages m where m.scan_id=s.scan_id);
select 'SCANS_WITH_WORKER_RUNS', count(distinct scan_id)::text from tenant_xbow.worker_runs;
