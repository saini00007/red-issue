#!/bin/bash
B=/var/lib/docker/volumes/abhedi_red_scanner_data/_data/16e69f07-f908-482b-8fc5-492852a61a91
echo "=== oob_interactions record KEYS + types (running scan, no payload values) ==="
sudo head -3 "$B/84aea81a-7e43-495c-9974-ca064ddd3552/oob_interactions.jsonl" 2>/dev/null | python3 -c "
import sys, json
for line in sys.stdin:
    o=json.loads(line)
    print({k: type(v).__name__ for k,v in o.items()})
"
echo "=== findings.jsonl: categories + verified + evidence presence (running) ==="
sudo cat "$B/84aea81a-7e43-495c-9974-ca064ddd3552/findings.jsonl" 2>/dev/null | python3 -c "
import sys, json, collections
c=collections.Counter(); ver=collections.Counter(); ev=0; n=0
for line in sys.stdin:
    line=line.strip()
    if not line: continue
    try: o=json.loads(line)
    except Exception: continue
    n+=1
    c[str(o.get('category') or o.get('vuln_class') or '?')]+=1
    ver['verified' if o.get('verified') else 'unverified']+=1
    if o.get('proof_of_concept') or o.get('evidence') or o.get('evidence_ids') or o.get('oob_token'): ev+=1
print('total:',n,'| by category:',c.most_common(15))
print('verified:',dict(ver),'| with evidence-ish field:',ev)
"
echo "=== same for long completed scan ==="
sudo cat "$B/1f5fe7c8-5e28-45bc-8e08-a3e868bad87e/findings.jsonl" 2>/dev/null | python3 -c "
import sys, json, collections
c=collections.Counter(); ver=collections.Counter(); ev=0; n=0
for line in sys.stdin:
    line=line.strip()
    if not line: continue
    try: o=json.loads(line)
    except Exception: continue
    n+=1
    c[str(o.get('category') or o.get('vuln_class') or '?')]+=1
    ver['verified' if o.get('verified') else 'unverified']+=1
    if o.get('proof_of_concept') or o.get('evidence') or o.get('evidence_ids') or o.get('oob_token'): ev+=1
print('total:',n,'| by category:',c.most_common(15))
print('verified:',dict(ver),'| with evidence-ish field:',ev)
"
echo "=== agent.log presence + first event names ==="
sudo find "$B/84aea81a-7e43-495c-9974-ca064ddd3552/logs" -type f 2>/dev/null | head
sudo grep -c "" "$B/84aea81a-7e43-495c-9974-ca064ddd3552/logs/agent.log" 2>/dev/null || echo "no agent.log"
sudo grep -cE "no choices|provider" "$B/84aea81a-7e43-495c-9974-ca064ddd3552/logs/agent.log" 2>/dev/null || true
echo "=== agent_messages roles for running scan ==="
docker exec -i scanner-postgres psql -U scanner -d scanner -P pager=off <<'SQL'
SET search_path TO tenant_xbow, public;
SELECT column_name FROM information_schema.columns WHERE table_schema='tenant_xbow' AND table_name='agent_messages' ORDER BY ordinal_position;
SQL
