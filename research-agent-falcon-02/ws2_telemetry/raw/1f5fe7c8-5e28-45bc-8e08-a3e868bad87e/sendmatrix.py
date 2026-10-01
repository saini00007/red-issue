#!/usr/bin/env python3
import requests, time
H = "www.infinity" + "capital" + ".bh"
B = "https://" + H
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
base = {"fname":"probe","lname":"sec","areacode":"973","tel":"5551234",
        "cname":"qa","subject":"hello","msg":"ICPROBE-MARKER","check":"on"}
s = requests.Session()
s.headers.update({"User-Agent":UA,"Accept":"*/*"})
def show(tag, r):
    print("%-28s %s len=%d mit=%s" % (tag, r.status_code, len(r.content), r.headers.get('x-vercel-mitigated')))
    print("    ", r.text[:300].replace("\n"," "))
# empty
show("empty", s.post(B+"/api/send", data={}, timeout=25))
time.sleep(1)
# full, no targets
b2 = dict(base); b2.pop("targets", None)
show("no_targets", s.post(B+"/api/send", data=b2, timeout=25))
time.sleep(1)
# full with targets json list of in-scope address
b3 = dict(base); b3["targets"] = '["probe@infinitycapital.bh"]'
show("with_targets", s.post(B+"/api/send", data=b3, timeout=25))
time.sleep(1)
# multipart
show("multipart", s.post(B+"/api/send", files={k:(None,v) for k,v in b3.items()}, timeout=25))
time.sleep(1)
# GET
r = s.get(B+"/api/send", timeout=25); show("GET", r)
