set -u
q() { docker exec scanner-postgres psql -U scanner -d scanner -X -A -F' | ' -t -c "$1" 2>&1; }
echo "=== U1 findings whose description/tool mentions a write failure (search text) ==="
q "select left(scan_id::text,8), count(*) from tenant_xbow.findings where coalesce(detected_by_tool,'') ilike '%permission denied%' or coalesce(verification_notes,'') ilike '%permission denied%' or coalesce(description,'') ilike '%permission denied%' group by 1;"
echo "=== U2 evidence_object rejection_reason census ==="
q "select left(coalesce(rejection_reason,'<NULL>'),70), count(*) from tenant_xbow.evidence_object group by 1 order by 2 desc limit 15;"
echo "=== U3 audit_log: error-ish actions ==="
q "select left(action,50), count(*) from tenant_xbow.audit_log group by 1 order by 2 desc limit 20;"
echo "=== U4 scan_events top event_type ==="
q "select left(event_type,44), count(*) from tenant_xbow.scan_events group by 1 order by 2 desc limit 25;"