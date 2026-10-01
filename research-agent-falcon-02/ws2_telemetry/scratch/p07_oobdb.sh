set -u
q() { docker exec scanner-postgres psql -U scanner -d scanner -X -A -F' | ' -t -c "$1" 2>&1; }
echo "=== I1 oob_token columns ==="
q "select column_name,data_type from information_schema.columns where table_schema='tenant_xbow' and table_name='oob_token' order by ordinal_position;"
echo "=== I2 oob_token totals ==="
q "select count(*), count(distinct scan_id), count(fired_at) from tenant_xbow.oob_token;"
echo "=== I3 oob_token per scan ==="
q "select left(scan_id::text,8), count(*) n, count(fired_at) fired, min(fired_at)::text, max(fired_at)::text from tenant_xbow.oob_token group by 1 order by 2 desc;"
echo "=== I4 evidence_object columns ==="
q "select column_name,data_type from information_schema.columns where table_schema='tenant_xbow' and table_name='evidence_object' order by ordinal_position;"
echo "=== I5 evidence totals ==="
q "select count(*), count(distinct scan_id) from tenant_xbow.evidence_object;"
echo "=== I6 findings columns ==="
q "select column_name,data_type from information_schema.columns where table_schema='tenant_xbow' and table_name='findings' order by ordinal_position;"