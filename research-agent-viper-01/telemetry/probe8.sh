#!/bin/bash
echo "=== oob_token schema + fired vs minted (recent scans) ==="
docker exec -i scanner-postgres psql -U scanner -d scanner -P pager=off <<'SQL'
SET search_path TO tenant_xbow, public;
SELECT column_name FROM information_schema.columns WHERE table_schema='tenant_xbow' AND table_name='oob_token' ORDER BY ordinal_position;
SQL
docker exec -i scanner-postgres psql -U scanner -d scanner -P pager=off <<'SQL'
SET search_path TO tenant_xbow, public;
SELECT scan_id, count(*) AS tokens FROM oob_token GROUP BY scan_id ORDER BY 2 DESC LIMIT 6;
SQL
echo "=== proxy calls schema + aggregate dist (NO bodies) ==="
sqlite3 -readonly /home/admin/research/2026-09-29-deepdive/proxy/data/proxy_log.db <<'SQL'
.headers on
SELECT name FROM sqlite_master WHERE type='table';
PRAGMA table_info(calls);
SELECT count(*) AS rows_total FROM calls;
SQL
