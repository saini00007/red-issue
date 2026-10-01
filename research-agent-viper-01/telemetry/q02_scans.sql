SET search_path TO tenant_xbow, public;
\dt
SELECT scan_id, status, target, mode, created_at, started_at, finished_at FROM scans ORDER BY created_at DESC LIMIT 15;
