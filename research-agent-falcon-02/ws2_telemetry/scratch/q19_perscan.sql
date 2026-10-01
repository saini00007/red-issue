select 'WR_SCAN_TABLE', scan_id::text, n::text, nerr::text, nempty::text, n429::text, st::text from (
  select w.scan_id, s.status as st, count(*) n,
         sum(case when w.status='error' then 1 else 0 end) nerr,
         sum(case when w.error ilike '%no choices%' or w.error ilike '%empty%' then 1 else 0 end) nempty,
         sum(case when w.error ilike '%429%' or w.error ilike '%rate limit%' then 1 else 0 end) n429
  from tenant_xbow.worker_runs w join tenant_xbow.scans s on s.scan_id=w.scan_id
  group by 1,2) t order by n desc limit 22;
select 'AM_PER_SCAN', scan_id::text, count(*)::text, count(distinct agent_id)::text, max(turn_index)::text
  from tenant_xbow.agent_messages group by 1 order by 2 desc limit 22;
select 'AM_MODELS', coalesce(model,'?'), count(*)::text from tenant_xbow.agent_messages group by 1 order by 2 desc limit 12;
select 'AM_TURNS_PER_AGENT_DIST', n::text, count(*)::text from (
  select agent_id, count(*) n from tenant_xbow.agent_messages group by 1) t group by 1 order by 1::int;
select 'WR_PHASE_DIST', coalesce(phase,'?'), count(*)::text from tenant_xbow.worker_runs group by 1 order by 2 desc limit 20;
