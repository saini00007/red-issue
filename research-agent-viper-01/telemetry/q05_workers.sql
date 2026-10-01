SET search_path TO tenant_xbow, public;
-- Q5a: worker_runs schema
SELECT column_name FROM information_schema.columns WHERE table_schema='tenant_xbow' AND table_name='worker_runs' ORDER BY ordinal_position;
-- Q5b: per-worker durations/status for the 915-min scan
SELECT worker_id, status, EXTRACT(EPOCH FROM (finished_at - started_at))/60 AS dur_min, tool_calls, error
FROM worker_runs WHERE scan_id='1f5fe7c8-5e28-45bc-8e08-a3e868bad87e' ORDER BY dur_min DESC NULLS LAST LIMIT 30;
-- Q5c: status distribution for that scan
SELECT status, count(*), round(avg(EXTRACT(EPOCH FROM (finished_at - started_at))/60),1) AS avg_dur_min
FROM worker_runs WHERE scan_id='1f5fe7c8-5e28-45bc-8e08-a3e868bad87e' GROUP BY status;
-- Q5d: same for the currently-running scan
SELECT status, count(*), round(avg(EXTRACT(EPOCH FROM (finished_at - started_at))/60),1) AS avg_dur_min
FROM worker_runs WHERE scan_id='84aea81a-7e43-495c-9974-ca064ddd3552' GROUP BY status;
-- Q5e: tool invocations over time for the long scan (hourly buckets)
SELECT date_trunc('hour', created_at) AS hr, count(*) FROM tool_invocations
WHERE scan_id='1f5fe7c8-5e28-45bc-8e08-a3e868bad87e' GROUP BY 1 ORDER BY 1;
