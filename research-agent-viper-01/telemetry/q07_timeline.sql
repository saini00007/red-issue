SET search_path TO tenant_xbow, public;
-- tool invocations over the 915-min scan, hourly
SELECT date_trunc('hour', started_at) AS hr, count(*), round(avg(EXTRACT(EPOCH FROM (finished_at-started_at))),1) AS avg_dur_s
FROM tool_invocations WHERE scan_id='1f5fe7c8-5e28-45bc-8e08-a3e868bad87e' GROUP BY 1 ORDER BY 1;
-- failure/sentinel distribution
SELECT exit_code, count(*) FROM tool_invocations WHERE scan_id='1f5fe7c8-5e28-45bc-8e08-a3e868bad87e' GROUP BY 1 ORDER BY 2 DESC LIMIT 10;
-- top tools
SELECT tool_name, count(*) FROM tool_invocations WHERE scan_id='1f5fe7c8-5e28-45bc-8e08-a3e868bad87e' GROUP BY 1 ORDER BY 2 DESC LIMIT 15;
-- findings + evidence counts for recent scans
SELECT s.scan_id, s.status,
  (SELECT count(*) FROM findings f WHERE f.scan_id=s.scan_id) AS findings,
  (SELECT count(*) FROM findings f WHERE f.scan_id=s.scan_id AND f.verified) AS verified_findings,
  (SELECT count(*) FROM evidence_object e WHERE e.scan_id=s.scan_id) AS evidence_objs,
  (SELECT count(*) FROM tool_invocations t WHERE t.scan_id=s.scan_id) AS tool_calls
FROM scans s ORDER BY s.created_at DESC LIMIT 8;
