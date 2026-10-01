set -u
q() { docker exec scanner-postgres psql -U scanner -d scanner -X -A -F' | ' -t -c "$1" 2>&1; }
echo "=== S1 exact duplicate commands overall ==="
q "select count(*) total, count(distinct command) distinct_cmd, count(*)-count(distinct command) dup_rows from tenant_xbow.tool_invocations;"
echo "=== S2 per-scan duplicate command rate ==="
q "select left(scan_id::text,8), count(*) n, count(distinct command) d, count(*)-count(distinct command) dup, round(100.0*(count(*)-count(distinct command))/count(*),1) pct from tenant_xbow.tool_invocations group by 1 order by dup desc limit 15;"
echo "=== S3 top duplicated commands (LENGTH + repeat count only, no content) ==="
q "select tool_name, length(command) cmd_len, count(*) n, count(distinct scan_id) scans from tenant_xbow.tool_invocations group by tool_name, length(command) order by n desc limit 20;"
echo "=== S4 duplicate rate EXCLUDING null/empty commands ==="
q "select count(*) filter (where command is not null and command<>'') real_cmds, count(distinct command) filter (where command is not null and command<>'') distinct_real from tenant_xbow.tool_invocations;"
echo "=== S5 output_summary duplication (same result re-fetched) ==="
q "select count(*) n, count(distinct md5(coalesce(output_summary,''))) d from tenant_xbow.tool_invocations where output_summary is not null and output_summary<>'';"
echo "=== S6 tool_invocations per agent: is one agent looping? ==="
q "select agent_id, count(*) n, count(distinct command) d from tenant_xbow.tool_invocations group by 1 order by n desc limit 12;"