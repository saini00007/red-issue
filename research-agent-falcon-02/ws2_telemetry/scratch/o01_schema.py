import os, json
ROOT="/var/lib/scanner"
H=None
for h in os.listdir(ROOT):
    p=os.path.join(ROOT,h)
    if os.path.isdir(p): H=p; break
subs=sorted(os.listdir(H))
d=os.path.join(H,subs[0])
print("sample workdir:", subs[0])
for fn in ["oob_health.json"]:
    p=os.path.join(d,fn)
    print("--",fn,"exists:",os.path.isfile(p))
    if os.path.isfile(p): print("   ", json.dumps(json.load(open(p)),indent=1)[:400])
for fn in ["oob_registry.jsonl","oob_interactions.jsonl","ledger_updates.jsonl","exploit_floor_signals.jsonl","findings.jsonl"]:
    p=os.path.join(d,fn)
    if not os.path.isfile(p): print("--",fn,"MISSING"); continue
    print("--",fn,"KEYS:", sorted(json.loads(open(p,encoding='utf-8',errors='replace').readline() or '{}').keys()))