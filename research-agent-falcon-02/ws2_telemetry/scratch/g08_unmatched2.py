import os, re, collections
ROOT="/var/lib/scanner"
HOST=[os.path.join(ROOT,h) for h in sorted(os.listdir(ROOT)) if os.path.isdir(os.path.join(ROOT,h))][0]
files=[]
for sid in sorted(os.listdir(HOST)):
    d=os.path.join(HOST,sid); p=os.path.join(d,"logs","agent.log")
    if os.path.isfile(p): files.append((sid,p))
kinds=collections.Counter()
per_scan=collections.Counter()
per_scan_kind=collections.defaultdict(collections.Counter)
RE=re.compile(r'ledger\.resolve\.([A-Za-z_]+)')
PLACE={"never-contacted-control","control-only-not-sent","local-control","none","(no target - control only)","control","n/a","-","unknown","placeholder"}
tot=0; ph_tot=0
for sid,p in files:
    for ln in open(p,encoding="utf-8",errors="replace"):
        if "ledger.resolve" not in ln: continue
        tot+=1
        m=RE.search(ln); k=m.group(1) if m else "?"
        kinds[k]+=1
        per_scan[sid[:8]]+=1
        per_scan_kind[sid[:8]][k]+=1
        ep=re.search(r'endpoint=(.*?)(?:\s+vuln_class=|$)',ln)
        e=(ep.group(1).strip().lower() if ep else "")
        if e in PLACE: ph_tot+=1; per_scan_kind[sid[:8]]["PLACEHOLDER"]+=1
print("=== ledger.resolve kinds (global) ===")
for k,v in kinds.most_common(): print("   %-22s %7d"%(k,v))
print("   TOTAL %d   placeholder-endpoint lines %d (%.1f%%)"%(tot,ph_tot,100*ph_tot/tot))
print()
print("=== per-scan counts (correct attribution) ===")
for sid,n in per_scan.most_common():
    br=", ".join("%s=%d"%(k,v) for k,v in per_scan_kind[sid].most_common())
    print("   %-10s %7d   %s"%(sid,n,br))