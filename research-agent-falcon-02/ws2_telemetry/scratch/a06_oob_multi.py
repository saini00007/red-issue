import json, collections, os, re

RAW = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + r"\raw"
SCANS = {
    "84aea81a(bunny,live)": RAW,
    "68a58881(nemotron)": os.path.join(RAW, "68a58881-ae3b-4f36-90a9-bf254da13fcb"),
    "1f5fe7c8(bunny)": os.path.join(RAW, "1f5fe7c8-5e28-45bc-8e08-a3e868bad87e"),
}

def jl(base, name):
    p = os.path.join(base, name)
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

print("#" * 74)
print("### Q2  OOB HONESTY  (multi-scan, from workdir artifacts)")
print("#" * 74)
for label, base in SCANS.items():
    print("\n---", label, "---")
    hp = os.path.join(base, "oob_health.json")
    health = {}
    if os.path.exists(hp):
        health = json.loads(open(hp, encoding="utf-8", errors="replace").read())
        print("  oob_health keys:", {k: (str(v)[:46]) for k, v in health.items()})

    reg = jl(base, "oob_registry.jsonl") or []
    inter = jl(base, "oob_interactions.jsonl") or []
    print("  registry tokens: %d | interactions: %d" % (len(reg), len(inter)))
    if reg:
        print("   registry token fmt samples:", [r.get("token") for r in reg[:3]])
        print("   registry keys:", sorted(reg[0].keys()) if reg else None)
        print("   registry HAS timestamp field:", any("time" in k or "at" == k[-2:] for k in (reg[0].keys() if reg else [])))
    if inter:
        print("   interaction keys:", sorted(inter[0].keys()))
        pref = collections.Counter()
        for it in inter:
            fid = str(it.get("full-id") or it.get("full_id") or "")
            pref[fid.split("-")[0] if fid else "(none)"] += 1
        print("   full-id prefix distribution:", dict(pref.most_common(12)))
        print("   protocols:", dict(collections.Counter(it.get("protocol") for it in inter).most_common()))
        uid = collections.Counter(str(it.get("unique-id")) for it in inter)
        print("   distinct unique-id:", len(uid), "-> top:", uid.most_common(3))

    # verdict/classification fields present?
    if inter:
        vk = set()
        for it in inter:
            vk.update(k for k in it.keys() if any(s in k.lower() for s in ("class", "verdict", "confirm", "state", "status", "honest")))
        print("   verdict-ish fields in interactions:", sorted(vk) or "NONE")

    # tokens registered vs tokens seen in interactions
    regtokens = {str(r.get("token")) for r in reg if r.get("token")}
    print("   registered tokens: %d distinct" % len(regtokens))
    if regtokens and inter:
        seen = set()
        for it in inter:
            for t in regtokens:
                if t and t in str(it.get("full-id") or "") or (t and t in str(it.get("unique-id") or "")):
                    seen.add(t)
        print("   registered tokens appearing in interactions: %d (%.1f%%)" % (len(seen), 100.0*len(seen)/len(regtokens)))
        print("   registered tokens NEVER seen in any interaction: %d" % (len(regtokens)-len(seen)))

    # pre-session callbacks: interaction ts < oob_health.checked_at
    chk = health.get("checked_at")
    if chk and inter:
        try:
            floor = datetime_floor = chk.replace("Z", "+00:00")
            import datetime as _dt
            fdt = _dt.datetime.fromisoformat(floor)
            pre = 0; post = 0; bad = 0
            for it in inter:
                ts = it.get("timestamp")
                if not ts:
                    bad += 1; continue
                try:
                    idt = _dt.datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
                except Exception:
                    bad += 1; continue
                if idt < fdt: pre += 1
                else: post += 1
            print("   PRE-SESSION callbacks (interaction ts < oob_health.checked_at): %d  [post=%d unparsable=%d]" % (pre, post, bad))
        except Exception as e:
            print("   floor parse failed:", e)

    # interaction ts ordering / duplicates
    if inter:
        tss = sorted(str(it.get("timestamp")) for it in inter if it.get("timestamp"))
        print("   interaction ts range:", tss[0], "->", tss[-1])
