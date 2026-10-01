SET search_path TO tenant_xbow, public;
-- Q6a: error distribution for the 915-min scan
SELECT error, count(*) AS n, round(avg(EXTRACT(EPOCH FROM (finished_at-started_at))/60),1) AS avg_dur
FROM worker_runs WHERE scan_id='1f5fe7c8-5e28-45bc-8e08-a3e868bad87e' AND status='error'
GROUP BY error ORDER BY n DESC LIMIT 15;
-- Q6b: findings/output per worker for that scan
SELECT status, count(*), sum(findings_count) AS findings, sum(resolved_count) AS resolved
FROM worker_runs WHERE scan_id='1f5fe7c8-5e28-45bc-8e08-a3e868bad87e' GROUP BY status;
-- Q6c: partial error reasons for that scan
SELECT error, count(*) FROM worker_runs WHERE scan_id='1f5fe7c8-5e28-45bc-8e08-a3e868bad87e' AND status='partial' GROUP BY 1;
-- Q6d: tool_invocations schema
SELECT column_name FROM information_schema.columns WHERE table_schema='tenant_xbow' AND table_name='tool_invocations' ORDER BY ordinal_position;
-- Q6e: errors for the running scan
SELECT error, count(*) FROM worker_runs WHERE scan_id='84aea81a-7e43-495c-9974-ca164ddd3552' AND status='error' GROUP BY 1 LIMIT 5;
SELECT left(error,120) AS err, count(*) FROM worker_runs WHERE scan_id='84aea81a-7e43-495c-9974-ca064ddd3552' AND status='error' GROUP BY 1;
SELECT left(error,120) AS err, count(*) FROM worker_runs WHERE scan_id='1f5fe7c8-5e28-45bc-8e08-a3e868bad87e' AND status='error' GROUP BY 1 ORDER BY 2 DESC LIMIT 10;
