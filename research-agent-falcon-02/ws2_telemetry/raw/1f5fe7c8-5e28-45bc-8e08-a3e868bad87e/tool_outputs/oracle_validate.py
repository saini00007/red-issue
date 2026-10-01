import json, collections
D = "/var/lib/scanner/16e69f07-f908-482b-8fc5-492852a61a91/1f5fe7c8-5e28-45bc-8e08-a3e868bad87e"

rows = [json.loads(l) for l in open(D + "/oob_interactions.jsonl")]
seen = collections.Counter()
for r in rows:
    q = (r.get("full-id") or "")
    seen[q.split(".")[0]] += 1

CTRL = ("totallyrandom", "control", "never", "deadbeef", "zzz", "zqx", "selftest")
orphans = {t: n for t, n in seen.items() if t.lower().startswith(CTRL)}

print("=== CONTROL tokens never sent to the target, yet they RECEIVED interactions ===")
for t, n in sorted(orphans.items(), key=lambda x: -x[1]):
    print("  %-40s interactions=%d" % (t, n))

print()
print("total control-token interactions:", sum(orphans.values()))
print("total interactions:", len(rows))
print()
print("VERDICT: a control hostname that was NEVER transmitted to the target still")
print("resolved and got a callback => wildcard DNS. The oracle CANNOT prove a")
print("blind SSRF/XXE/RFI. All prior 'confirmed via OOB' findings on this target")
print("are unsupported.")
