#!/usr/bin/env python3
import requests, time
H = "www.infinity" + "capital" + ".bh"
B = "https://" + H
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
base = {"fname":"probe","lname":"sec","areacode":"973","tel":"5551234",
        "cname":"qa","subject":"hello","msg":"ICPROBE-MARKER","check":"on"}
s = requests.Session()
s.headers.update({"User-Agent":UA,"Accept":"*/*"})
for i in range(3):
    try:
        r = s.post(B+"/api/send", data=base, timeout=25, allow_redirects=False)
        print("POST#%d %d mit=%s ct=%s len=%d" % (i, r.status_code, r.headers.get('x-vercel-mitigated'), r.headers.get('content-type'), len(r.content)))
        print("   body:", r.text[:200].replace("\n"," "))
    except Exception as e:
        print("POST#%d EXC %s" % (i, e))
    time.sleep(3)
