import requests, sys, time, json
S = requests.Session()
S.headers.update({
 "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
 "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
 "Accept-Language":"en-US,en;q=0.9",
})
B="https://www.infinitycapital.bh"
def hit(tag, path, **kw):
    try:
        r = S.get(B+path, timeout=40, allow_redirects=False, **kw)
        print(f"{tag:14s} {r.status_code} len={len(r.content):7d} ct={r.headers.get('content-type','')[:40]:40s} mit={r.headers.get('x-vercel-mitigated','')} mp={r.headers.get('x-matched-path','')}")
        open(f"d10b/{tag}.bin","wb").write(r.content)
        open(f"d10b/{tag}.hdr","w").write(str(r.headers))
        return r
    except Exception as e:
        print(f"{tag:14s} ERR {e}")
        return None
for tag,path in [
    ("home","/"),
    ("contact","/contact"),
    ("send","/api/send"),
    ("img_valid","/_next/image?url="+"https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg"+"&w=1080&q=75"),
    ("robots","/robots.txt"),
    ("sitemap","/sitemap.xml"),
]:
    hit(tag,path); time.sleep(1.5)
