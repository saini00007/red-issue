import os, json, collections
ROOT="/var/lib/scanner"
HOST=[os.path.join(ROOT,h) for h in sorted(os.listdir(ROOT)) if os.path.isdir(os.path.join(ROOT,h))][0]
def jl(p):
    if not os.path.isfile(p): return []
    o=[]
    for ln in open(p,encoding="utf-8",errors="replace"):
        ln=ln.strip()
        if ln:
            try: o.append(json.loads(ln))
            except Exception: pass
    return o
kc=collections.Counter(); tot=0; srcs=collections.Counter()
for sid in sorted(os.listdir(HOST)):
    d=os.path.join(HOST,sid)
    if not os.path.isdir(d): continue
    for r in jl(os.path.join(d,"ledger_updates.jsonl")):
        tot+=1; kc.update(r.keys())
        srcs[str(r.get("source") or r.get("by") or r.get("actor") or "")[:24]]+=1
print("ledger_updates rows:",tot)
print("KEYS:",dict(kc))
print("source/by census:",srcs.most_common(12))