import os, re, collections
ROOT="/var/lib/scanner"
HOST=[os.path.join(ROOT,h) for h in sorted(os.listdir(ROOT)) if os.path.isdir(os.path.join(ROOT,h))][0]
files=[]
for sid in sorted(os.listdir(HOST)):
    d=os.path.join(HOST,sid); p=os.path.join(d,"logs","agent.log")
    if os.path.isfile(p): files.append((sid,d,p))

# tool.started lines carry a command-ish signature; measure exact repeat rate
SIG=re.compile(r'event_type=tool\.started(.*)')
def cmd_sig(seg):
    # keep structural tokens only; redact values
    s=re.sub(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}','<uuid>',seg)
    s=re.sub(r'oob[0-9a-f]{6,}','<oobtok>',s)
    s=re.sub(r'\b\d{2,}\b','<n>',s)
    s=re.sub(r"'[^']{8,}'", "'<v>'", s)
    return re.sub(r'\s+',' ',s).strip()[:220]

exact=collections.Counter()      # identical full command string
shape=collections.Counter()
per_scan_dup=collections.Counter()
per_scan_tot=collections.Counter()
TOOL=re.compile(r'tool_name=([A-Za-z0-9_.:-]+)')
for sid,d,p in files:
    ex=collections.Counter(); sh=collections.Counter()
    for ln in open(p,encoding="utf-8",errors="replace"):
        if "event_type=tool.started" not in ln: continue
        seg=SIG.search(ln).group(1) if SIG.search(ln) else ""
        t=TOOL.search(ln)
        key=(t.group(1) if t else "?")
        ex[(key,seg.strip()[:200])]+=1
        sh[(key,cmd_sig(seg))]+=1
    per_scan_tot[sid[:8]]=sum(ex.values())
    for k,v in ex.items(): exact[k]+=v
    for k,v in sh.items(): shape[k]+=v
    per_scan_dup[sid[:8]]=sum(v-1 for v in ex.values() if v>1)

tot=per_scan_tot and sum(per_scan_tot.values())
duprows=sum(v-1 for v in exact.values() if v>1)
print("=== RETRY / DUPLICATE-WORK ANALYSIS (tool.started events, shape+exact) ===")
print("total tool.started analysed: %d"%tot)
print("exact-duplicate repeats (same tool + identical cmd): %d  (%.1f%%)"%(duprows,100*duprows/tot))
sh_dup=sum(v-1 for v in shape.values() if v>1)
print("shape-duplicate repeats (same tool + normalized cmd): %d  (%.1f%%)"%(sh_dup,100*sh_dup/tot))
print()
print("=== top 25 most-repeated exact (tool,cmd) — counts only, values redacted ===")
for (t,c),v in exact.most_common(25):
    if v>1: print("   %-10s x%-5d  %s"%(t,v,c[:120]))
print()
print("=== per-scan duplicate rate (exact) ===")
for sid in sorted(per_scan_tot, key=lambda s:-per_scan_dup[s])[:12]:
    t=per_scan_tot[sid]; d_=per_scan_dup[sid]
    print("   %-10s tools=%-7d dup=%-7d (%.1f%%)"%(sid,t,d_,100*d_/t if t else 0))