import requests, json, urllib.parse
B="https://www.infinitycapital.bh"
H={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15"}
BID="h8L2LlI5LSORU50iQ3wJq"
paths=[
 f"/_next/data/{BID}/index.json",
 f"/_next/data/{BID}/contact.json",
 f"/_next/data/{BID}/404.json",
 f"/_next/data/{BID}/api.json",
 f"/_next/static/{BID}/_buildManifest.js",
 f"/_next/static/{BID}/_ssgManifest.js",
 "/_next/routes-manifest.json",
 "/_next/server/app-paths-manifest.json",
 "/_next/server/middleware-manifest.json",
 "/_next/server/pages-manifest.json",
 "/_next/server/functions-config-manifest.json",
 "/.next/routes-manifest.json",
 "/_next/image?url=assets/img/logo.png&w=256&q=75",
]
for p in paths:
    try:
        r=requests.get(B+p,headers=H,timeout=25,allow_redirects=False)
        ct=r.headers.get('content-type','')
        print(f"{r.status_code} {len(r.content):7d} {ct[:30]:32s} {p}")
        if r.status_code==200 and ('json' in ct or 'javascript' in ct):
            print("      >>",r.content[:400])
    except Exception as e: print("ERR",p,e)
