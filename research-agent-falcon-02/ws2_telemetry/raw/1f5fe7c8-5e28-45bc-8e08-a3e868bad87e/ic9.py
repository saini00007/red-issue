#!/usr/bin/env python3
import requests, json, sys, time
S = requests.Session()
S.headers.update({
 "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
 "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
 "Accept-Language":"en-US,en;q=0.9",
 "sec-ch-ua":'"Chromium";v="126", "Not;A=Brand";v="24"',
 "sec-fetch-dest":"document","sec-fetch-mode":"navigate","sec-fetch-site":"none",
 "Upgrade-Insecure-Requests":"1",
})
BASE="https://www.infinitycapital.bh"
def get(p, tries=12):
    r=None
    for i in range(tries):
        r=S.get(BASE+p, timeout=25)
        if r.status_code!=403 or "Vercel Security Checkpoint" not in r.text:
            return r
        time.sleep(0.4)
    return r
def api(p, method="GET", **kw):
    h=dict(S.headers); h.update({"Accept":"*/*",
      "sec-fetch-dest":"empty","sec-fetch-mode":"cors","sec-fetch-site":"same-origin"})
    h.pop("Upgrade-Insecure-Requests",None)
    r=None
    for i in range(12):
        r=S.request(method, BASE+p, headers=h, timeout=25, **kw)
        if "Vercel Security Checkpoint" not in r.text:
            return r
        time.sleep(0.4)
    return r
def send(**over):
    d={"fname":"ICTEST","lname":"Probe","areacode":"973","tel":"5551234",
       "cname":"vapt.probe.zz9@example.com","subject":"General Inquiry",
       "msg":"ic-probe-9","check":"false","targets":""}
    d.update(over)
    return api("/api/send","POST",data=d)
def jprint(r,label):
    try: body=r.json()
    except Exception: body=r.text[:600]
    print(f"[{label}] HTTP {r.status_code} :: {json.dumps(body)[:900] if isinstance(body,dict) else body}")
    return body
