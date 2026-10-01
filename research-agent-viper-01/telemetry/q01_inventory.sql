\dn
SELECT scan_id, status, target, mode, created_at, started_at, finished_at FROM public.scans ORDER BY created_at DESC LIMIT 15;
