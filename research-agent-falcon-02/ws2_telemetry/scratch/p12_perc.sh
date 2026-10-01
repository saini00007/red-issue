set -u
q() { docker exec scanner-postgres psql -U scanner -d scanner -X -A -F' | ' -t -c "$1" 2>&1; }
echo "=== P1 per-scan: msgs / worker_runs / tool_calls / findings / cells ==="
q "select left(s.scan_id::text,8), s.status,
 (select count(*) from tenant_xbow.agent_messages m where m.scan_id=s.scan_id) msgs,
 (select count(*) from tenant_xbow.worker_runs w where w.scan_id=s.scan_id) wruns,
 (select count(*) from tenant_xbow.tool_invocations t where t.scan_id=s.scan_id) tools,
 (select count(*) from tenant_xbow.findings f where f.scan_id=s.scan_id) fnd,
 (select count(*) from tenant_xbow.ledger_cell l where l.scan_id=s.scan_id) cells
 from tenant_xbow.scans s where s.status in ('completed','partial') order by tools desc;"
echo "=== P2 cost accounting ==="
q "select 'agent_messages cost_usd nonzero', count(*)::text from tenant_xbow.agent_messages where coalesce(cost_usd,0)<>0 union all select 'scans cost_spent sum', coalesce(sum(cost_spent_usd),0)::text from tenant_xbow.scans union all select 'scans cost_spent nonzero', count(*)::text from tenant_xbow.scans where coalesce(cost_spent_usd,0)<>0 union all select 'scans cost_cap nonzero', count(*)::text from tenant_xbow.scans where coalesce(cost_cap_usd,0)<>0;"
echo "=== P3 tokens_in/out census ==="
q "select 'msg tokens_in=0', count(*)::text from tenant_xbow.agent_messages where coalesce(tokens_in,0)=0 union all select 'msg tokens_out=0', count(*)::text from tenant_xbow.agent_messages where coalesce(tokens_out,0)=0 union all select 'msg sum tokens_in', sum(coalesce(tokens_in,0))::text from tenant_xbow.agent_messages union all select 'msg sum tokens_out', sum(coalesce(tokens_out,0))::text from tenant_xbow.agent_messages;"
echo "=== P4 proxy tokens for comparison (nemotron scans only) ==="
q "select 'note: see proxy db' , '0';"
echo "=== P5 worker_runs: findings_count vs actual findings (bookkeeping drift) ==="
q "select sum(coalesce(w.findings_count,0)) as wr_declared, (select count(*) from tenant_xbow.findings) as fnd_actual from tenant_xbow.worker_runs w;"
echo "=== P6 ledger_cell state census ==="
q "select coalesce(state,'<NULL>'), count(*) from tenant_xbow.ledger_cell group by 1 order by 2 desc limit 20;"
echo "=== P7 ledger_cell: cells resolved to a finding ==="
q "select count(*) filter (where finding_id is not null) with_finding, count(*) filter (where evidence_ids is not null) with_evidence, count(*) total from tenant_xbow.ledger_cell;"