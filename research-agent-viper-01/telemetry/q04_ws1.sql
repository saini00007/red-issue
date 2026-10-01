SET search_path TO tenant_xbow, public;
-- Q4a: scan durations (recent 12)
SELECT scan_id, status, mode,
       EXTRACT(EPOCH FROM (completed_at - started_at))/60 AS dur_min,
       time_cap_seconds/60 AS cap_min
FROM scans ORDER BY created_at DESC LIMIT 12;
-- Q4b: ledger cell state census per recent scan
SELECT scan_id, state, applicable, count(*),
       round(avg(attempts),2) AS avg_attempts, max(attempts) AS max_attempts
FROM ledger_cell WHERE scan_id IN (SELECT scan_id FROM scans ORDER BY created_at DESC LIMIT 8)
GROUP BY scan_id, state, applicable ORDER BY scan_id, state;
-- Q4c: claimed-cell forensics — who holds cells, and how long stale
SELECT scan_id, claimed_by, count(*) AS n,
       count(*) FILTER (WHERE lease_expires_at < now()) AS lease_expired
FROM ledger_cell
WHERE claimed_by IS NOT NULL AND scan_id IN (SELECT scan_id FROM scans ORDER BY created_at DESC LIMIT 8)
GROUP BY scan_id, claimed_by ORDER BY scan_id, n DESC;
