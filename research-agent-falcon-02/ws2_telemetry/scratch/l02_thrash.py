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

print("### Q1  LEDGER STATE THRASH — aggregate over all 43 workdirs")
print()
# state census
st=collections.Counter(); trans=collections.Counter(); per_cell_counts=[]
osc_cells=0; cells_total=0; revisits=0; rows=0
backtrack=collections.Counter()   # transitions that move AWAY from a terminal state
terminal={"confirmed","closed","not_applicable","na","rejected","excluded","resolved"}
# evidence-length by state (work magnitude proxy)
ev_by_state=collections.defaultdict(list)
scans_with=0
for sid in sorted(os.listdir(HOST)):
    d=os.path.join(HOST,sid)
    if not os.path.isdir(d): continue
    rows_=jl(os.path.join(d,"ledger_updates.jsonl"))
    if not rows_: continue
    scans_with+=1
    seq=collections.defaultdict(list)
    for r in rows_:
        rows+=1
        key=(str(r.get("endpoint","")).strip(), str(r.get("vuln_class","")).strip())
        s=str(r.get("state","")).strip()
        st[s]+=1
        seq[key].append(s)
        ev=r.get("evidence")
        n = len(ev) if isinstance(ev,(list,dict,str)) else (0 if ev is None else 1)
        ev_by_state[s].append(n)
    for key,ss in seq.items():
        cells_total+=1
        per_cell_counts.append(len(ss))
        # transitions
        for a,b in zip(ss,ss[1:]): trans[(a,b)]+=1
        # revisits: a state seen more than once in the sequence
        cnt=collections.Counter(ss)
        if any(v>1 for v in cnt.values()): revisits+=1
        # oscillation: >=2 returns to a state already left
        seen=set(); ret=0
        for x in ss:
            if x in seen: ret+=1
            seen.add(x)
        if ret>=2: osc_cells+=1
        # backtrack out of a terminal state
        for a,b in zip(ss,ss[1:]):
            if a in terminal: backtrack[(a,b)]+=1
per_cell_counts.sort()
print("workdirs with ledger_updates:", scans_with)
print("total ledger rows:", rows)
print("distinct cells touched:", cells_total)
print("updates per cell: p50=%d p90=%d p99=%d max=%d mean=%.2f"%(
    per_cell_counts[len(per_cell_counts)//2], per_cell_counts[int(len(per_cell_counts)*.9)],
    per_cell_counts[int(len(per_cell_counts)*.99)], per_cell_counts[-1],
    sum(per_cell_counts)/len(per_cell_counts)))
print()
print("=== STATE CENSUS (rows) ===")
for k,v in st.most_common(): print("   %-18s %6d  %5.1f%%"%(k,v,100*v/rows))
print()
print("=== TOP 25 TRANSITIONS (from->to) ===")
tot_tr=sum(trans.values())
for (a,b),v in trans.most_common(25):
    print("   %-18s -> %-18s %6d  %5.1f%% of transitions"%(a,b,v,100*v/tot_tr))
print()
print("distinct transitions:", len(trans), " total transitions:", tot_tr)
print("cells with a REPEATED state (revisit): %d (%.1f%%)"%(revisits,100*revisits/cells_total))
print("cells with >=2 returns to an already-left state (oscillation): %d (%.1f%%)"%(osc_cells,100*osc_cells/cells_total))
print()
print("=== BACKTRACK OUT OF TERMINAL STATE (correctness red flag) ===")
for (a,b),v in backtrack.most_common(15): print("   %-18s -> %-18s %5d"%(a,b,v))
print()
print("=== EVIDENCE-MAGNITUDE BY STATE (work proxy; mean items) ===")
for k in sorted(ev_by_state, key=lambda x:-len(ev_by_state[x])):
    v=sorted(ev_by_state[k]); print("   %-18s n=%6d mean=%.2f p50=%d p90=%d"%(k,len(v),sum(v)/len(v),v[len(v)//2],v[int(len(v)*.9)]))