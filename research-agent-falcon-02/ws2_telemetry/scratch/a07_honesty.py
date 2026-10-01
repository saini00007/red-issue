import json, collections, os, datetime as dt

RAW = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + r"\raw"
LIVE = RAW
SCANS = [
    ("84aea81a", "bunny/openrouter", LIVE, "scan_84aea81a_oob_registry.jsonl", "scan_84aea81a_oob_interactions.jsonl", None),
    ("68a58881", "nemotron", os.path.join(RAW, "68a58881-ae3b-4f36-90a9-bf254da13fcb"), "oob_registry.jsonl", "oob_interactions.jsonl", "oob_health.json"),
    ("1f5fe7c8", "bunny", os.path.join(RAW, "1f5fe7c8-5e28-45bc-8e08-a3e868bad87e"), "oob_registry.jsonl", "oob_interactions.jsonl", "oob_health.json"),
]

def jl(p):
    if not os.path.exists(p):
        return None
    out = []
    for line in open(p, encoding="utf-8", errors="replace"):
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    return out

def ts(x):
    try:
        return dt.datetime.fromisoformat(str(x).replace("Z", "+00:00"))
    except Exception:
        return None

print("### Q2 HONESTY MATRIX  identity_present x session_scoped")
print("%-10s %-16s %8s %8s %10s %10s %12s" % ("scan", "model", "inter", "ident?", "pre-sess", "post-sess", "PASS_GATE"))
tot = collections.Counter()
for sid, model, base, rname, iname, hname in SCANS:
    inter = jl(os.path.join(base, iname)) or []
    health = {}
    if hname and os.path.exists(os.path.join(base, hname)):
        health = json.loads(open(os.path.join(base, hname), encoding="utf-8", errors="replace").read())
    floor = ts(health.get("checked_at")) if health.get("checked_at") else None
    reg = jl(os.path.join(base, rname)) or []
    regtok = {str(r.get("token")).lower() for r in reg if r.get("token")}

    n = len(inter)
    ident = 0
    pre = 0
    post = 0
    passed = 0
    matched_registered = 0
    for it in inter:
        raw = it
        i = str(raw.get("unique-id") or raw.get("unique_id") or raw.get("full-id") or raw.get("full_id") or "").strip()
        t = ts(raw.get("timestamp"))
        has_id = bool(i)
        if has_id:
            ident += 1
        if t is not None and floor is not None:
            if t < floor:
                pre += 1
            else:
                post += 1
        # replicate registry.correlate gate
        if has_id:
            if floor is None or (t is not None and t >= floor):
                passed += 1
        fid = str(raw.get("full-id") or "").lower()
        if any(tk and tk in fid for tk in regtok):
            matched_registered += 1
    print("%-10s %-16s %8d %8d %10d %10d %12d" % (sid, model, n, ident, pre, post, passed))
    print("           registered tokens=%d ; interactions whose full-id contains a REGISTERED token=%d (%.2f%%)"
          % (len(regtok), matched_registered, 100.0*matched_registered/n if n else 0))
    tot["inter"] += n; tot["ident"] += ident; tot["pre"] += pre; tot["post"] += post; tot["passed"] += passed
    tot["reg"] += len(regtok); tot["matched"] += matched_registered
print("\nTOTALS over 3 workdirs: interactions=%d identity_present=%d (%.1f%%) pre_session=%d (%.1f%%) pass_both_gates=%d (%.1f%%)"
      % (tot["inter"], tot["ident"], 100.0*tot["ident"]/tot["inter"], tot["pre"], 100.0*tot["pre"]/tot["inter"],
         tot["passed"], 100.0*tot["passed"]/tot["inter"]))
print("registered tokens total=%d ; interactions matching a registered token=%d (%.2f%% of interactions)"
      % (tot["reg"], tot["matched"], 100.0*tot["matched"]/tot["inter"]))
