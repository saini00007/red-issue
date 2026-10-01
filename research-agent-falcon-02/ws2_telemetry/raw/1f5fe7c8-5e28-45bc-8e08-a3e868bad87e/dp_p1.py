import json, sys, time, requests
sys.path.insert(0, ".")
from dp_lib import S, B, go, show

# Which paths actually reach the origin vs get edge-mitigated?
probe = ["/api/send", "/api/contact", "/contact", "/atom.xml", "/feeds/all.atom.xml",
         "/_next/image?w=640&q=75", "/api/", "/sitemap.xml", "/404", "/favicon.ico",
         "/_next/static/chunks/main.js", "/.env", "/.git/HEAD", "/api/send?x=1"]
for p in probe:
    r = go(p, pace=7)
    if isinstance(r, Exception):
        print(f"{p[:60]:62} EXC {r}")
        continue
    print(f"{p[:60]:62} {r.status_code} len={len(r.content):7} "
          f"mit={r.headers.get('x-vercel-mitigated','-'):5} "
          f"mp={r.headers.get('x-matched-path','-')[:30]:30} ct={r.headers.get('content-type','-')[:28]}")
