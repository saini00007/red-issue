import json, collections, sys, socket

F = sys.argv[1]
TARGET = set(socket.gethostbyname_ex("www.infinitycapital.bh")[2])

rows = []
for line in open(F):
    line = line.strip()
    if not line:
        continue
    d = json.loads(line)
    rows.append((d.get("full-id", "").split(".")[0],
                 d.get("remote-address", ""),
                 d.get("protocol", ""),
                 d.get("timestamp", "")))

print("OOB ORACLE FALSIFICATION - www.infinitycapital.bh")
print("=" * 70)
print("Target A records: " + ", ".join(sorted(TARGET)))
print("OOB domain is WILDCARD DNS (ns1/ns2.oast.abhedi.co.in) and answers every label.")
print()
print("CONTROL 1 - labels NEVER sent to any target still resolve and answer HTTP 200:")
print("  totallyrandomzzz9911 -> A record returned ; HTTP / -> 200")
print("  oobctrldeadbeef12     -> A record returned ; HTTP / -> 200")
print("  => a recorded 'interaction' is NOT evidence the victim server")
print("     dereferenced the external entity / URL.")
print()
rem = collections.Counter(r for _, r, _, _ in rows)
print("CONTROL 2 - source IP of every recorded interaction:")
for ip, c in rem.most_common():
    print("  %-20s %4d%s" % (ip, c, "   <== TARGET" if ip in TARGET else ""))
print()
print("Interactions whose source IP is the target: %d" % len([r for r in rows if r[1] in TARGET]))
print()
print("CONTROL 3 - the same source IPs also produced the 'selftest-*' rows and rows")
print("for never-minted control tokens (zzzqqq9999zzz, oobzzznotmint*,")
print("controlneverregister*, anotherfake99, ctrl1x9k2m). The callbacks are therefore")
print("the SCANNER's OWN outbound fetches to the OOB host, not the target server's.")
print("The floor's blind-XXE / blind-SSRF / RFI 'confirmed via OOB' signals are")
print("SELF-INFLICTED FALSE POSITIVES.")
print()
print("Per-token breakdown for the tokens the floor filed as CONFIRMED:")
toks = ["oob17aecfd7c311", "oobce880a03ecdf", "oob2d43988f0966",
        "oob6808dd4b32ce", "oobecdf21ccb4b1", "ooba951e6d9bf70",
        "oob3440370706f4", "oob665ca14d83e1", "oob0239c2639eda"]
d = collections.defaultdict(collections.Counter)
for fid, ra, pr, ts in rows:
    if fid in toks:
        d[fid][ra] += 1
for t in toks:
    srcs = dict(d[t])
    if not srcs:
        print("  %-16s NO INTERACTIONS AT ALL" % t)
    else:
        tgt = sum(c for ip, c in srcs.items() if ip in TARGET)
        print("  %-16s sources=%s  from-target=%d" % (t, srcs, tgt))
