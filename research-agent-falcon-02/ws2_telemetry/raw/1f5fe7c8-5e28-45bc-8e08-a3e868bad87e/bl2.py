from curl_cffi import requests as cr
import time
B = "https://www.infinitycapital.bh"
S = cr.Session(impersonate="chrome124")
for i in range(6):
    r = S.get(B + "/", timeout=35, allow_redirects=False)
    print(i, r.status_code, len(r.content), r.headers.get("x-vercel-mitigated"))
    if r.status_code == 200:
        print("OK title:", r.text[r.text.find("<title>"):r.text.find("</title>") + 8])
        break
    time.sleep(8)