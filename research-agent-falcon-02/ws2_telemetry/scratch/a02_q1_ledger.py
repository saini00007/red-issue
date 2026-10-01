import json, collections, os, re

RAW = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + r"\raw"

def load(name):
    out = []
    with open(os.path.join(RAW, name), "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out

lu = load("scan_84aea81a_ledger_updates.jsonl")

print("### Q1 LEDGER THRASH")
print("total ledger_updates rows:", len(lu))
print("state distribution:", dict(collections.Counter(r["state"] for r in lu)))
meth = collections.Counter()
for r in lu:
    for m in r.get("methods", []):
        meth[m.split(":")[0]] += 1
print("method prefixes:", dict(meth))
print("vuln_class distribution:", dict(collections.Counter(r["vuln_class"] for r in lu).most_common()))

# cell identity
cells = collections.defaultdict(list)
for i, r in enumerate(lu):
    cells[(r["endpoint"], r["vuln_class"])].append((i, r))
print("distinct cells (endpoint,vuln_class):", len(cells))

# floor-owned = method prefix exploit_floor
def is_floor(r):
    return any(m.startswith("exploit_floor") for m in r.get("methods", []))

floor_cells = {k: v for k, v in cells.items() if any(is_floor(r) for _, r in v)}
print("cells touched by exploit_floor:", len(floor_cells))
print("cells NOT touched by exploit_floor:", len(cells) - len(floor_cells))

# transitions: count cells where state changes after first non-'testing'/'untested' entry
def osc_score(seq):
    """number of state changes after the first observation"""
    states = [s for s in seq]
    changes = sum(1 for a, b in zip(states, states[1:]) if a != b)
    return changes

rows_per_cell = collections.Counter(len(v) for v in cells.values())
print("rows-per-cell histogram:", dict(sorted(rows_per_cell.items())))

osc = collections.Counter()
osc_floor = collections.Counter()
osc_nofloor = collections.Counter()
for k, v in cells.items():
    seq = [r["state"] for _, r in v]
    c = osc_score(seq)
    osc[c] += 1
    (osc_floor if k in floor_cells else osc_nofloor)[c] += 1
print("state-changes-per-cell histogram (ALL):", dict(sorted(osc.items())))
print("state-changes-per-cell (FLOOR cells):", dict(sorted(osc_floor.items())))
print("state-changes-per-cell (NON-floor cells):", dict(sorted(osc_nofloor.items())))

# dominant oscillation pattern: most common state sequence (compressed run-length)
def rle(seq):
    out = []
    for s in seq:
        if out and out[-1][0] == s:
            out[-1][1] += 1
        else:
            out.append([s, 1])
    return tuple(s for s, n in out)

pat = collections.Counter(rle([r["state"] for _, r in v]) for v in cells.values())
print("distinct state patterns:", len(pat))
for p, n in pat.most_common(12):
    print("   n=%-4d %s" % (n, " -> ".join(p)))

# oscillation among patterns that revisit a state (A->...->A)
revisit = [(k, v) for k, v in cells.items()
           if len(set(r["state"] for _, r in v)) < len([r["state"] for _, r in v])]
print("cells that REVISIT a prior state (>=1 oscillation):", len(revisit),
      "= %.1f%%" % (100.0 * len(revisit) / len(cells)))
print("cells with >=3 distinct states:", sum(1 for v in cells.values()
      if len(set(r["state"] for _, r in v)) >= 3))
