#!/bin/bash
sqlite3 -readonly /home/admin/research/2026-09-29-deepdive/proxy/data/proxy_log.db <<'SQL'
.headers on
SELECT substr(ts,1,10) AS day, count(*) AS calls, count(DISTINCT model_fwd) AS models FROM calls GROUP BY 1 ORDER BY 1 DESC LIMIT 8;
SELECT model_fwd, count(*) AS n, round(avg(latency_ms)) AS avg_ms, count(*) FILTER (WHERE status>=500) AS errs
FROM calls GROUP BY model_fwd ORDER BY n DESC LIMIT 15;
SELECT endpoint, count(*) FROM calls GROUP BY endpoint ORDER BY 2 DESC LIMIT 6;
SELECT count(*) FILTER (WHERE status>=500) AS server_errs, count(*) FILTER (WHERE status=429) AS rate_limited, count(*) AS total FROM calls;
SQL
