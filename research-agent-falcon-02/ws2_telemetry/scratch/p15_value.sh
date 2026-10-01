set -u
q() { docker exec scanner-postgres psql -U scanner -d scanner -X -A -F' | ' -t -c "$1" 2>&1; }
echo "=== T1 exploit_floor share of all tool calls ==="
q "select sum(case when agent_id='exploit_floor' then 1 else 0 end) floor, count(*) tot, round(100.0*sum(case when agent_id='exploit_floor' then 1 else 0 end)/count(*),1) pct from tenant_xbow.tool_invocations;"
echo "=== T2 findings by detected_by_agent / detected_by_tool ==="
q "select coalesce(detected_by_agent,'<NULL>'), count(*) from tenant_xbow.findings group by 1 order by 2 desc limit 12;"
q "select coalesce(detected_by_tool,'<NULL>'), count(*) from tenant_xbow.findings group by 1 order by 2 desc limit 12;"
echo "=== T3 findings from exploit_floor vs LLM ==="
q "select case when detected_by_tool like 'exploit_floor%' then 'exploit_floor(deterministic)' when verification_method like 'exploit_floor%' then 'exploit_floor(verif)' when verification_method='oob_callback' then 'oob_callback' when verification_method='deferred_canary' then 'deferred_canary' else 'llm_or_manual' end src, count(*), count(*) filter (where verified) v from tenant_xbow.findings group by 1 order by 2 desc;"
echo "=== T4 agent_messages per scan vs tool calls (value test) ==="
q "select left(s.scan_id::text,8),
 (select count(*) from tenant_xbow.agent_messages m where m.scan_id=s.scan_id) msgs,
 (select count(*) from tenant_xbow.tool_invocations t where t.scan_id=s.scan_id) tools,
 (select count(*) from tenant_xbow.findings f where f.scan_id=s.scan_id) fnd
 from tenant_xbow.scans s where s.status in ('completed','partial') order by msgs desc;"
echo "=== T5 scans with ZERO agent_messages but tool calls >0 ==="
q "select count(*) from tenant_xbow.scans s where (select count(*) from tenant_xbow.tool_invocations t where t.scan_id=s.scan_id)>0 and (select count(*) from tenant_xbow.agent_messages m where m.scan_id=s.scan_id)=0;"