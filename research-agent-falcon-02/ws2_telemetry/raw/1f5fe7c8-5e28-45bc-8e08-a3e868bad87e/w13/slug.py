import sys, re, json, urllib.parse
sys.path.insert(0,"w13")
from sess import req, B

MARK="ZZMARK9XZQ"
paths = [
 "/"+MARK, "/"+MARK+"/", "/insights", "/insights/", "/blog", "/news",
 "/services", "/team", "/portfolio", "/privacy", "/terms",
 "/_next/static/"+MARK, "/api/"+MARK, "/contact/"+MARK,
]
for p in paths:
    r=req(p)
    t=r.text or ""
    ti=re.search(r"<title>([^<]*)",t)
    loc=r.headers.get("location","-")
    print(f"{r.status_code:4} len={len(t):7} loc={loc[:60]:60} title={ti.group(1) if ti else None} :: {p}")

print()
print("=== robots.txt")
r=req("/robots.txt"); print(r.status_code); print(r.text[:800])
print()
print("=== sitemap-index.xml (follow)")
r=req("/sitemap-index.xml", allow_redirects=True); print(r.status_code, len(r.text))
print(r.text[:1500])
