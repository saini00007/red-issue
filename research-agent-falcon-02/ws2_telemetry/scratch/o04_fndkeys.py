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
kc=collections.Counter(); n=0
for sid in sorted(os.listdir(HOST)):
    d=os.path.join(HOST,sid)
    if not os.path.isdir(d): continue
    for f in jl(os.path.join(d,"findings.jsonl")):
        n+=1; kc.update(f.keys())
print("total findings.jsonl rows:", n)
for k,v in kc.most_common(40): print("  %-28s %d"%(k,v))
# any token-ish field?
print()
print("token-ish keys present:", [k for k in kc if "token" in k.lower() or "oob" in k.lower()])
# category census
cat=collections.Counter()
for sid in sorted(os.listdir(HOST)):
    d=os.path.join(HOST,sid)
    if not os.path.isdir(d): continue
    for f in jl(os.path.join(d,"findings.jsonl")):
        cat[str(f.get("category"))[:22]]+=1
print("category census (top 20):")
for k,v in cat.most_common(20): print("  %-24s %d"%(k,v))