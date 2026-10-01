import json, collections, os

RAW = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + r"\raw"

def load(name):
    out, bad = [], 0
    with open(os.path.join(RAW, name), "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                bad += 1
    return out, bad

for name in ["scan_84aea81a_ledger_updates.jsonl", "scan_84aea81a_oob_interactions.jsonl",
             "scan_84aea81a_oob_registry.jsonl", "scan_84aea81a_findings.jsonl",
             "scan_84aea81a_exploit_floor_signals.jsonl"]:
    rows, bad = load(name)
    keys = collections.Counter()
    for r in rows:
        if isinstance(r, dict):
            keys.update(r.keys())
    print("=" * 70)
    print(name, "rows=", len(rows), "unparsable=", bad)
    print("  keys:", dict(keys.most_common(30)))
    if rows and isinstance(rows[0], dict):
        for k, v in list(rows[0].items())[:14]:
            sv = repr(v)
            print(f"   {k} = {sv[:150]}")
