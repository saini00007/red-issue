set -u
q() { docker exec scanner-postgres psql -U scanner -d scanner -X -A -F' | ' -t -c "$1" 2>&1; }
echo "=== M1 agent_messages columns ==="
q "select column_name,data_type from information_schema.columns where table_schema='tenant_xbow' and table_name='agent_messages' order by ordinal_position;"
echo "=== M2 totals ==="
q "select count(*), count(distinct scan_id), count(distinct agent_id) from tenant_xbow.agent_messages;"
echo "=== M3 role census ==="
q "select coalesce(role,'<NULL>'), count(*) from tenant_xbow.agent_messages group by 1 order by 2 desc;"
echo "=== M4 worker_runs columns ==="
q "select column_name,data_type from information_schema.columns where table_schema='tenant_xbow' and table_name='worker_runs' order by ordinal_position;"
echo "=== M5 tool_invocations columns ==="
q "select column_name,data_type from information_schema.columns where table_schema='tenant_xbow' and table_name='tool_invocations' order by ordinal_position;"