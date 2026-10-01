import os, re, collections
ROOT="/var/lib/scanner"
HOST=[os.path.join(ROOT,h) for h in sorted(os.listdir(ROOT)) if os.path.isdir(os.path.join(ROOT,h))][0]
files=[]
for sid in sorted(os.listdir(HOST)):
    d=os.path.join(HOST,sid); p=os.path.join(d,"logs","agent.log")
    if os.path.isfile(p): files.append((sid,p))
kinds=collections.Counter(); scans=collections.defaultdict(set)
ph=collections.Counter()          # placeholder endpoints (non-real)
vuln=collections.Counter()
RE=re.compile(r'\[(warning|error)\s*\]\s+(ledger\.resolve\.[A-Za-z_]+)')
RE2=re.compile(r'ledger\.resolve\.([A-Za-z_]+)')
VUL=re.compile(r'vuln_class=([A-Za-z0-9_]+)')
tot=0
PLACE={"NEVER-CONTACTED-CONTROL","CONTROL-ONLY-NOT-SENT","local-control","none","(no target - control only)",
       "control","CONTROL","n/a","-","unknown","placeholder"}
for sid,p in files:
    for ln in open(p,encoding="utf-8",errors="replace"):
        if "ledger.resolve" not in ln: continue
        tot+=1
        m=RE.search(ln) or RE2.search(ln)
        k=("warning:" if "[warning" in ln else "error:")+(m.group(1) if m else "?")
        kinds[k]+=1; scans[k].add(sid[:8])
        ep=re.search(r'endpoint=(.*?)(?:\s+vuln_class=|$)',ln)
        e=(ep.group(1).strip() if ep else "")
        if e in PLACE or e.lower() in {x.lower() for x in PLACE}:
            ph[k]+=1
        v=VUL.search(ln)
        if v: vuln[v.group(1)]+=1
print("=== ledger.resolve.* event kinds (aggregate) ===")
for k,v in kinds.most_common(): print("   %-46s %7d scans=%2d  placeholder_ep=%d"%(k,v,len(scans[k]),ph[k]))
print("   TOTAL:",tot)
print()
print("=== of which endpoint is an explicit NON-TARGET placeholder (never a real finding) ===")
tp=sum(ph.values()); print("   %d of %d (%.1f%%)"%(tp,tot,100*tp/tot))
print()
print("=== vuln_class on unmatched findings ===")
for k,v in vuln.most_common(15): print("   %-22s %7d"%(k,v))
print()
print("=== scans affected (top) ===")
agg=collections.Counter()
for k,s in scans.items():
    for x in s: agg[x]+=kinds[k]
for k,v in agg.most_common(15): print("   %-10s %7d"%(k,v))