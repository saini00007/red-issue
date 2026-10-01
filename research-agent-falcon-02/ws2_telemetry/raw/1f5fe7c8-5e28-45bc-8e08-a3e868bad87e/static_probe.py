#!/usr/bin/env python3
import requests
B = "https://" + "www.infinity" + "capital" + ".bh"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
paths = [
 "/_next/static/chunks/main.js",
 "/_astro/index.astro",
 "/favicon.ico",
 "/_next/image",
 "/api/send",
 "/index.html",
 "/_vercel/insights/view",
 "/_headers",
 "/.well-known/security.txt",
]
for p in paths:
    try:
        r = requests.get(B+p, headers={"User-Agent":UA}, timeout=20, allow_redirects=False)
        print(f"{p:45} {r.status_code} mit={r.headers.get('x-vercel-mitigated')} ct={r.headers.get('content-type')} len={len(r.content)}")
    except Exception as e:
        print(p, "EXC", e)
