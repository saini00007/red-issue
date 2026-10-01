#!/usr/bin/env python3
import requests, re, json
B="https://www.infinitycapital.bh"
s=requests.Session()
s.headers.update({"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"})
h=s.get(B+"/",timeout=30).text
open("home.html","w").write(h)
js=sorted(set(re.findall(r'/_next/static/[A-Za-z0-9_./\-]+\.js', h)))
print("JS refs in HTML:", len(js))
for u in js: print(" ", u)
# fetch build manifest / app build manifest
cands=["/_next/static/"+m for m in re.findall(r'buildManifest[^"]*', h)]
print("manifest cands", cands)
alljs=set(js)
for u in list(js):
    t=s.get(B+u,timeout=30).text
    alljs.update(B+x for x in re.findall(r'/_next/static/[A-Za-z0-9_./\-]+\.js', t))
    apis=set(re.findall(r'["\'](/api/[A-Za-z0-9_./\-]*)["\']', t))
    if apis: print("API in",u,apis)
print("total unique js:",len(alljs))
# look for route manifest
for u in alljs:
    if "routes" in u or "manifest" in u:
        print("CAND",u)
# dump all api-like strings
found=set()
for u in alljs:
    t=s.get(u,timeout=30).text
    found.update(re.findall(r'/api/[A-Za-z0-9_./\-]{1,60}', t))
print("=== all /api/ strings in JS ===")
for f in sorted(found): print(" ",f)
