SET search_path TO tenant_xbow, public;
SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='tenant_xbow' AND table_name='scans' ORDER BY ordinal_position;
SELECT scan_id, status, created_at FROM scans ORDER BY created_at DESC LIMIT 15;
