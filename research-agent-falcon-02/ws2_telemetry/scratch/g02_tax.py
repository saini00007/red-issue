import os, re, collections
ROOT="/var/lib/scanner"
HOST=[os.path.join(ROOT,h) for h in sorted(os.listdir(ROOT)) if os.path.isdir(os.path.join(ROOT,h))][0]
files=[]
for sid in sorted(os.listdir(HOST)):
    d=os.path.join(HOST,sid); p=os.path.join(d,"logs","agent.log")
    if os.path.isfile(p): files.append((sid,p))
print("agent.log files:",len(files))

# event.published style: event_type=xxx  -> primary classifier
ev=collections.Counter(); ev_scan=collections.defaultdict(set)
lvl=collections.Counter()
ERRLINE=re.compile(r'\b(ERROR|CRITICAL|WARNING)\b')
# error classes: normalized signature (digits/hex/uuid scrubbed)
def sig(t):
    t=re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}','<uuid>',t)
    t=re.sub(r'\b\d{3,}\b','<n>',t)
    t=re.sub(r'[0-9a-f]{12,}','<hex>',t)
    t=re.sub(r'\s+',' ',t).strip()
    return t[:150]
errsigs=collections.Counter(); errsig_scan=collections.defaultdict(set)
toolserver=collections.Counter()
tot=0
for sid,p in files:
    for ln in open(p,encoding="utf-8",errors="replace"):
        tot+=1
        m=re.search(r'event_type=([A-Za-z0-9_.]+)',ln)
        if m:
            k=m.group(1); ev[k]+=1; ev_scan[k].add(sid[:8])
        for L in re.findall(r'\[(debug|info|warning|error|critical)\s*\]',ln):
            lvl[L]+=1
        if ERRLINE.search(ln):
            s=sig(ln)
            # strip timestamp+level prefix for grouping
            s=re.sub(r'^\S+\s+','',s)
            errsigs[s]+=1; errsig_scan[s].add(sid[:8])
print("total lines:",tot)
print()
print("=== LOG LEVELS ===")
for k,v in lvl.most_common(): print("   %-10s %8d"%(k,v))
print()
print("=== TOP 45 event_type (event.published) ===")
for k,v in ev.most_common(45):
    print("   %-42s %7d  scans=%d"%(k,v,len(ev_scan[k])))
print()
print("distinct event_type:",len(ev))
print()
print("=== ERROR/WARNING LINE SIGNATURES — top 40 (redacted, normalized) ===")
for k,v in errsigs.most_common(40):
    print("   %7d scans=%-3d %s"%(v,len(errsig_scan[k]),k[:130]))
print()
print("distinct error-line signatures:",len(errsigs))
import json
json.dump({"events":{k:[v,len(ev_scan[k])] for k,v in ev.items()},
           "levels":dict(lvl),
           "errsigs":{k:[v,len(errsig_scan[k])] for k,v in errsigs.most_common(400)},
           "total_lines":tot,"files":len(files)},
          open("/tmp/ws2_logtax.json","w"))
print("saved /tmp/ws2_logtax.json")