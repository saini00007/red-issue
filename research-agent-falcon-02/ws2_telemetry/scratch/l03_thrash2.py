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
print("### Q1b  Separating HEARTBEAT (same-state, no new evidence) from REAL THRASH")
heart=0; same_state_new_ev=0; real_retest=0; reopened=0; rows=0
cycles=collections.Counter(); scan_thrash=collections.Counter()
per_cell_reopen=collections.Counter()
for sid in sorted(os.listdir(HOST)):
    d=os.path.join(HOST,sid)
    if not os.path.isdir(d): continue
    rs=jl(os.path.join(d,"ledger_updates.jsonl"))
    if not rs: continue
    seq=collections.defaultdict(list)
    for r in rs:
        rows+=1
        seq[(str(r.get("endpoint","")).strip(), str(r.get("vuln_class","")).strip())].append(
            (str(r.get("state","")).strip(), r.get("evidence")))
    for key,ss in seq.items():
        for (a,ea),(b,eb) in zip(ss,ss[1:]):
            if a==b:
                same=json.dumps(ea,sort_keys=True)==json.dumps(eb,sort_keys=True)
                if same: heart+=1
                else: same_state_new_ev+=1
            elif b=="testing":     # re-entered testing after leaving it = real rework
                real_retest+=1; scan_thrash[sid[:8]]+=1
                reopened += 1 if a!="testing" else 0
print("total rows:",rows)
print("same-state re-append, IDENTICAL evidence (pure heartbeat):", heart)
print("same-state re-append, CHANGED evidence:", same_state_new_ev)
print("transitions back INTO testing (real rework events):", real_retest)
print("  of which from a NON-testing state (cell reopened):", reopened)
print("scans showing rework, top:", scan_thrash.most_common(12))
print()
# how much wasted tool work? correlate: cells reopened >1x
multi=collections.Counter()
for sid in sorted(os.listdir(HOST)):
    d=os.path.join(HOST,sid)
    if not os.path.isdir(d): continue
    rs=jl(os.path.join(d,"ledger_updates.jsonl"))
    seq=collections.defaultdict(list)
    for r in rs: seq[(str(r.get("endpoint","")).strip(),str(r.get("vuln_class","")).strip())].append(str(r.get("state","")).strip())
    for key,ss in seq.items():
        n=sum(1 for a,b in zip(ss,ss[1:]) if b=="testing" and a!="testing")
        if n: multi[sid[:8]]+=n
print("scans with >=1 reopened cell:", len(multi))
print("worst scans by reopened-cell count:", multi.most_common(10))