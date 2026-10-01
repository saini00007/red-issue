#!/usr/bin/env python3
"""W19g: pull the real /api/send call shape from the shipped JS."""
import re, time, urllib.request, urllib.error, urllib.parse

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
BASE = "https://www.infinitycapital.bh"


def get(url, timeout=25):
    r = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:
        return 0, str(e).encode()


st, b = get(BASE + "/contact")
html = b.decode("utf-8", "replace")
print(f"contact page: {st} {len(b)}B")
srcs = sorted(set(re.findall(r'src="([^"]+\.js[^"]*)"', html)))
print(f"{len(srcs)} script srcs")
open("/tmp/w19g_contact.html", "w").write(html)

# also grab any inline fetch calls
for m in re.finditer(r'fetch\((.{0,200})', html):
    print("INLINE FETCH:", m.group(0)[:200].replace("\n", " "))

seen = []
for s in srcs:
    u = s if s.startswith("http") else BASE + s
    st2, js = get(u)
    if st2 != 200:
        print(f"  {st2} {s}")
        continue
    txt = js.decode("utf-8", "replace")
    hits = []
    for pat in [r'/api/send', r'api/send', r'targets', r'multipart', r'FormData',
                r'newsletter', r'/api/', r'fetch\(']:
        if re.search(pat, txt):
            hits.append(pat)
    if hits:
        print(f"  HIT {s} ({len(js)}B) patterns={hits}")
        seen.append((s, txt))
    time.sleep(1.0)

print(f"\n=== detailed context from {len(seen)} matching bundles ===")
for s, txt in seen:
    for m in re.finditer(r'/api/send', txt):
        a, bnd = max(0, m.start() - 400), min(len(txt), m.end() + 400)
        print(f"\n--- {s} @ {m.start()} ---")
        print(txt[a:bnd])
    for m in re.finditer(r'FormData', txt):
        a, bnd = max(0, m.start() - 300), min(len(txt), m.end() + 500)
        print(f"\n--- FormData {s} @ {m.start()} ---")
        print(txt[a:bnd])
        break
