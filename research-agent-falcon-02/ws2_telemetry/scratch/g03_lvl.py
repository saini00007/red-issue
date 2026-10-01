import os, re, collections
ROOT="/var/lib/scanner"
HOST=[os.path.join(ROOT,h) for h in sorted(os.listdir(ROOT)) if os.path.isdir(os.path.join(ROOT,h))][0]
files=[]
for sid in sorted(os.listdir(HOST)):
    d=os.path.join(HOST,sid); p=os.path.join(d,"logs","agent.log")
    if os.path.isfile(p): files.append((sid,p))
LEVELS=re.compile(r'\[(debug|info|warning|error|critical)\s*\]')
def sig(t):
    t=re.sub(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}','<uuid>',t)
    t=re.sub(r'\b\d{3,}\b','<n>',t)
    t=re.sub(r'\b[0-9a-fA-F]{16,}\b','<hex>',t)
    t=re.sub(r'\b\d{1,3}(\.\d{1,3}){3}\b','<ip>',t)
    return re.sub(r'\s+',' ',t).strip()
lv=collections.Counter(); msg_by_lv=collections.defaultdict(collections.Counter)
msg_scan=collections.defaultdict(collections.defaultdict(set))
for sid,p in files:
    for ln in open(p,encoding="utf-8",errors="replace"):
        for L in LEVELS.findall(ln):
            lv[L]+=1
            body=ln.split("]",1)[-1]
            m=re.search(r'event_type=([A-Za-z0-9_.]+)',ln)
            key=(m.group(1) if m else body.strip()[:90])
            msg_by_lv[L][key]+=1
            msg_scan[L][key].add(sid[:8])
print("=== LEVEL COUNTS ===")
for k,v in lv.most_common(): print("   %-10s %8d"%(k,v))
for L in ("error","warning"):
    print()
    print("=== %s-level messages — top 30 ==="%L.upper())
    for k,v in msg_by_lv[L].most_common(30):
        print("   %6d scans=%-3d %s"%(v,len(msg_scan[L][k]),k[:125]))
    print("   distinct:",len(msg_by_lv[L]))
import json
json.dump({L:{k:[v,len(msg_scan[L][k])] for k,v in msg_by_lv[L].most_common(300)} for L in ("error","warning")},
          open("/tmp/ws2_lvl.json","w"))