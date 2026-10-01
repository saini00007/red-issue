#!/bin/bash
B=/var/lib/docker/volumes/abhedi_red_scanner_data/_data/16e69f07-f908-482b-8fc5-492852a61a91
echo "=== WS2: oob_interactions classification histogram (running scan) ==="
sudo cat "$B/84aea81a-7e43-495c-9974-ca064ddd3552/oob_interactions.jsonl" 2>/dev/null | python3 -c "
import sys, json, collections
c=collections.Counter(); kinds=collections.Counter()
for line in sys.stdin:
    line=line.strip()
    if not line: continue
    try: o=json.loads(line)
    except Exception: continue
    c[str(o.get('classification') or o.get('verdict') or 'unknown')]+=1
    kinds[str(o.get('protocol') or o.get('source') or o.get('kind') or 'unknown')]+=1
print('classification:', dict(c))
print('protocol/source:', dict(kinds))
"
echo "=== WS2: same for completed long scan ==="
sudo cat "$B/1f5fe7c8-5e28-45bc-8e08-a3e868bad87e/oob_interactions.jsonl" 2>/dev/null | python3 -c "
import sys, json, collections
c=collections.Counter()
for line in sys.stdin:
    line=line.strip()
    if not line: continue
    try: o=json.loads(line)
    except Exception: continue
    c[str(o.get('classification') or o.get('verdict') or 'unknown')]+=1
print('classification:', dict(c))
"
echo "=== WS2: ledger_updates histogram (running scan) ==="
sudo cat "$B/84aea81a-7e43-495c-9974-ca064ddd3552/ledger_updates.jsonl" 2>/dev/null | python3 -c "
import sys, json, collections
st=collections.Counter(); cl=collections.Counter()
for line in sys.stdin:
    line=line.strip()
    if not line: continue
    try: o=json.loads(line)
    except Exception: continue
    st[str(o.get('state') or '?')]+=1
    cl[str(o.get('vuln_class') or '?')]+=1
print('states:', dict(st))
print('top classes:', cl.most_common(12))
"
echo "=== WS2: agent.log error histograms (running scan) ==="
sudo ls -la "$B/84aea81a-7e43-495c-9974-ca064ddd3552/logs/" 2>/dev/null
sudo grep -oE "event=\"[a-z_.]+\"|\"event\": ?\"[a-z_.]+\"|max_turns_exceeded|no choices|context.{0,20}(reset|overflow|exceed)|rate.?limit|429|500|502" "$B/84aea81a-7e43-495c-9974-ca064ddd3552/logs/agent.log" 2>/dev/null | sort | uniq -c | sort -rn | head -25
echo "=== WS2: agent_messages turn counts per worker (running) ==="
docker exec -i scanner-postgres psql -U scanner -d scanner -P pager=off <<'SQL'
SET search_path TO tenant_xbow, public;
SELECT count(*) AS msgs, count(DISTINCT agent_id) AS agents, round(avg(cnt),1) AS avg_turns, max(cnt) AS max_turns
FROM (SELECT agent_id, count(*) AS cnt FROM agent_messages WHERE scan_id='84aea81a-7e43-495c-9974-ca064ddd3552' GROUP BY agent_id) t;
SQL
