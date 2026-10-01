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
    for i in range(tries):
        r=S.get(BASE+p, timeout=25)
        if r.status_code!=403 or "Vercel Security Checkpoint" not in r.text:
            return r
        time.sleep(0.4)
    return r
def api(p, method="GET", **kw):
    h=dict(S.headers); h.update({"Accept":"*/*","Content-Type":"application/x-www-form-urlencoded",
      "sec-fetch-dest":"empty","sec-fetch-mode":"cors","sec-fetch-site":"same-origin"})
    h.pop("Upgrade-Insecure-Requests",None)
    for i in range(12):
        r=S.request(method, BASE+p, headers=h, timeout=25, **kw)
        if "Vercel Security Checkpoint" not in r.text:
            return r
        time.sleep(0.4)
    return r
if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument("path"); ap.add_argument("-m",default="GET")
    ap.add_argument("-d",default=None); ap.add_argument("-o",default=None)
    a=ap.parse_args()
    kw={}
    if a.d: kw["data"]=a.d
    r=api(a.path,a.m,**kw) if not a.o else S.request(a.m,BASE+a.o,timeout=25)
    if a.m=="GET" and a.o: r=get(a.o)
    print(r.status_code, len(r.content), r.headers.get("content-type"))
    open("/work/d9_out.txt","wb").write(r.content)
    sys.stdout.write(r.text[:4000])
