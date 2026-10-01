import os, re, collections, json
ROOT="/var/lib/scanner"
HOST=[os.path.join(ROOT,h) for h in sorted(os.listdir(ROOT)) if os.path.isdir(os.path.join(ROOT,h))][0]
files=[]
for sid in sorted(os.listdir(HOST)):
    d=os.path.join(HOST,sid); p=os.path.join(d,"logs","agent.log")
    if os.path.isfile(p): files.append((sid,p))
LEVELS=re.compile(r'\[(debug|info|warning|error|critical)\s*\]')
lv=collections.Counter()
msg=collections.defaultdict(collections.Counter)
scans=collections.defaultdict(lambda: collections.defaultdict(set))
for sid,p in files:
    for ln in open(p,encoding="utf-8",errors="replace"):
        found=LEVELS.findall(ln)
        if not found: continue
        L=found[-1]
        lv[L]+=1
        body=ln.split("]",1)[-1]
        m=re.search(r'event_type=([A-Za-z0-9_.]+)',ln)
        key=m.group(1) if m else body.strip()[:90]
        msg[L][key]+=1
        scans[L][key].add(sid[:8])
print("=== LEVEL COUNTS ===")
for k,v in lv.most_common(): print("   %-10s %8d"%(k,v))
for L in ("error","warning"):
    print()
    print("=== %s-level messages - top 30 ==="%L.upper())
    for k,v in msg[L].most_common(30):
        print("   %6d scans=%-3d %s"%(v,len(scans[L][k]),k[:125]))
    print("   distinct:",len(msg[L]))
json.dump({L:dict((k,[v,len(scans[L][k])]) for k,v in msg[L].most_common(400)) for L in msg},
          open("/tmp/ws2_lvl.json","w"))
print("saved")