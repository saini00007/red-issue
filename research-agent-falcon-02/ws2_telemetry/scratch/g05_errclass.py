import os, re, collections
ROOT="/var/lib/scanner"
HOST=[os.path.join(ROOT,h) for h in sorted(os.listdir(ROOT)) if os.path.isdir(os.path.join(ROOT,h))][0]
files=[]
for sid in sorted(os.listdir(HOST)):
    d=os.path.join(HOST,sid); p=os.path.join(d,"logs","agent.log")
    if os.path.isfile(p): files.append((sid,p))

classes=collections.Counter(); scans=collections.defaultdict(set)
# normalize: event family only (strip the endpoint= payload)
EV=re.compile(r'event_type=([A-Za-z0-9_.]+)')
def fam(ln):
    m=EV.search(ln); return m.group(1) if m else None
tot=0
# error classes from verification.failed / worker failures
errcls=collections.Counter(); errscan=collections.defaultdict(set)
def classify_err(e):
    e=e.lower()
    if "max turns" in e: return "max_turns_exceeded"
    if "no choices" in e: return "no_choices"
    if "429" in e: return "http_429_rate_limit"
    if "500" in e: return "http_500_upstream"
    if "timeout" in e: return "timeout"
    if "context" in e and "length" in e: return "context_length"
    if "connection" in e or "connect" in e: return "connection_error"
    if "json" in e or "decode" in e: return "json_decode"
    return "other:"+re.sub(r'\d+','<n>',e)[:60]
for sid,p in files:
    for ln in open(p,encoding="utf-8",errors="replace"):
        tot+=1
        f=fam(ln)
        if f and (f.startswith("ledger.resolve") or "unmatched" in f):
            classes[f]+=1; scans[f].add(sid[:8])
        if "verification.failed" in ln or "worker.failed" in ln or "close_sweep.failed" in ln or "floor.failed" in ln:
            m=re.search(r'error=(.*)$',ln)
            e=m.group(1) if m else ""
            c=classify_err(e)
            errcls[c]+=1; errscan[c].add(sid[:8])
print("=== LEDGER-RESOLVE WARNING CLASSES (aggregate, payload stripped) ===")
for k,v in classes.most_common(30): print("   %-40s %7d scans=%d"%(k,v,len(scans[k])))
print("   TOTAL ledger.resolve warnings:", sum(classes.values()))
print()
print("=== ERROR CLASSES (normalized across all agent.log) ===")
for k,v in errcls.most_common(30): print("   %-40s %7d scans=%d"%(k,v,len(errscan[k])))
print("   TOTAL classified error events:", sum(errcls.values()))
print()
print("total lines:",tot)
# rate
print()
print("=== RATES ===")
print("ledger.resolve.*_unmatched as %% of all log lines: %.2f%%"%(100*sum(classes.values())/tot))