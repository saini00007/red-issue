import re, collections, os

RAW = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + r"\raw"
lines = [l.strip() for l in open(os.path.join(RAW, "scan_84aea81a_decisions.log"), encoding="utf-8", errors="replace") if l.strip()]
print("TOTAL decision records:", len(lines))

pat = re.compile(r"^\[(?P<agent>[^\]]+?)·turn(?P<turn>\d+)\]\s*(?P<reason>.*)$")
recs, unparsed = [], []
for l in lines:
    m = pat.match(l)
    if m:
        recs.append((m.group("agent"), int(m.group("turn")), m.group("reason").strip()))
    else:
        unparsed.append(l)

print("parsed:", len(recs), "unparsed:", len(unparsed))
if unparsed:
    print("UNPARSED SAMPLES:", unparsed[:5])

print("\nTERMINATION REASON DISTRIBUTION:")
for r, n in collections.Counter(x[2] for x in recs).most_common():
    print("  %-30s %d  (%.1f%%)" % (r, n, 100.0*n/len(recs)))

print("\nDISTINCT WORKERS:", len(set(a for a,_,_ in recs)))
print("TURNS SEEN:", dict(sorted(collections.Counter(t for _,t,_ in recs).items())))
print("MAX TURN NUMBER:", max(t for _,t,_ in recs))
print("TURNS PER WORKER DIST:", dict(sorted(collections.Counter(
    collections.Counter(a for a,_,_ in recs).values()).items())))

# worker-name families
fam = collections.Counter()
for a,_,_ in recs:
    fam[a.split("-")[0]] += 1
print("WORKER NAME FAMILIES:", dict(fam.most_common()))

# prefix patterns reveal prescribed rails
print("\nWORKER NAME PATTERN SHAPES (normalised):")
shape = collections.Counter(re.sub(r"\d+", "N", a) for a,_,_ in recs)
for s, n in shape.most_common(25):
    print("  %-46s %d" % (s, n))
