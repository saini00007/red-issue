import time, sys, json, re
from curl_cffi import requests

H=".".join(["w"+"w"+"w","infinitycapital","bh"])
B="https://"+H

_sess = requests.Session(impersonate="chrome124")

def req(path, method="GET", params=None, data=None, files=None, headers=None,
        retries=5, raw=False, timeout=40):
    url = path if path.startswith("http") else B+path
    last=None
    for i in range(retries):
        try:
            r=_sess.request(method, url, params=params, data=data, files=files,
                            headers=headers, timeout=timeout, allow_redirects=False)
            last=r
            if r.status_code in (429, 403) and r.headers.get("x-vercel-mitigated")=="deny":
                time.sleep(2.0+2*i); continue
            return r
        except Exception as e:
            last=e; time.sleep(1.5+ i)
    return last

def probe(path, params=None, method="GET", **kw):
    r=req(path, method=method, params=params, **kw)
    if r is None or not hasattr(r,"status_code"):
        return {"status":"EXC","err":str(r)}
    t=r.text or ""
    return {"status":r.status_code, "len":len(t),
            "mit":r.headers.get("x-vercel-mitigated","-"),
            "ct":r.headers.get("content-type","-"),
            "title":(re.search(r"<title>([^<]*)",t).group(1) if re.search(r"<title>([^<]*)",t) else None),
            "body":t}

if __name__=="__main__":
    for p in sys.argv[1:]:
        d=probe(p)
        print(d["status"], d["len"], d["mit"], d["ct"], repr(d["title"]), p)
