select 'AM_PER_SCAN', a.scan_id::text, count(*)::text, count(distinct a.agent_id)::text, max(a.turn_index)::text
  from tenant_xbow.agent_messages a group by a.scan_id order by 2 desc limit 22;
select 'AM_MODELS', coalesce(model,'?') as mdl, count(*)::text from tenant_xbow.agent_messages group by coalesce(model,'?') order by 2 desc limit 12;
select 'AM_TURNS_PER_AGENT_DIST', t.n::text, count(*)::text from (
  select a.agent_id, count(*) n from tenant_xbow.agent_messages a group by a.agent_id) t group by t.n order by 1::int;
select 'WR_PHASE_DIST', coalesce(w.phase,'?') as ph, count(*)::text from tenant_xbow.worker_runs w group by coalesce(w.phase,'?') order by 2 desc limit 20;
select 'COMPLETED_BUT_ALL_ERROR', count(*)::text from (
  select w.scan_id, sum(case when w.status='error' then 1 else 0 end) ne, count(*) n
  from tenant_xbow.worker_runs w join tenant_xbow.scans s on s.scan_id=w.scan_id
  where s.status in ('completed','partial') group by w.scan_id) t where t.ne = t.n;
select 'COMPLETED_TOTAL_WITH_RUNS', count(*)::text from (
  select w.scan_id from tenant_xbow.worker_runs w join tenant_xbow.scans s on s.scan_id=w.scan_id
  where s.status in ('completed','partial') group by w.scan_id) t;
select 'COMPLETED_100PCT_EMPTY', count(*)::text from (
  select w.scan_id, sum(case when w.error ilike '%no choices%' or w.error ilike '%empty%' then 1 else 0 end) ne, count(*) n
  from tenant_xbow.worker_runs w join tenant_xbow.scans s on s.scan_id=w.scan_id
  where s.status in ('completed','partial') group by w.scan_id) t where t.ne = t.n;
select 'FINDINGS_TOTAL', count(*)::text from tenant_xbow.findings;
select 'FINDINGS_VERIFIED', verified::text, count(*)::text from tenant_xbow.findings group by verified;
select 'FINDINGS_BY_SCAN_TOP', f.scan_id::text, count(*)::text,
       sum(case when f.verified then 1 else 0 end)::text
  from tenant_xbow.findings f group by f.scan_id order by 2 desc limit 15;
