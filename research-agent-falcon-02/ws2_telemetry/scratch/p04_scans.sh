set -u
q() { docker exec scanner-postgres psql -U scanner -d scanner -X -A -F' | ' -t -c "$1" 2>&1; }
echo "=== B1 scans columns ==="
q "select column_name, data_type from information_schema.columns where table_schema='tenant_xbow' and table_name='scans' order by ordinal_position;"
echo "=== B2 scans total by status ==="
q "select coalesce(status,'<NULL>'), count(*) from tenant_xbow.scans group by 1 order by 2 desc;"
echo "=== B3 scans total + time range ==="
q "select count(*), min(created_at), max(created_at) from tenant_xbow.scans;"