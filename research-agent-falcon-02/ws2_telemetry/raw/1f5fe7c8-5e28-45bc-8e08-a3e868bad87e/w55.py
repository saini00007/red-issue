import requests, urllib.parse, time
B="https://www.infinitycapital.bh"
H={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15"}
# 1) follow the /api redirect chain
for p in ["/api","/api/","/api?id=1","/api?id={{7*7}}"]:
    r=requests.get(B+p,headers=H,timeout=25,allow_redirects=True)
    print("GET",p,"->",r.status_code,r.url,len(r.content),r.headers.get('content-type'))
    for hk,hv in r.history: print("     hist",hk.status_code,hk.headers.get('location'))
print("--- POST probes to /api")
for p in ["/api","/api/","/api?id=1"]:
    for body in ['','id=1','{"id":1}','id={{7*7}}','{"name":"{{7*7}}"}']:
        r=requests.post(B+p,headers=dict(H,**{"Content-Type":"application/json" if body.startswith("{") else "application/x-www-form-urlencoded"}),data=body,timeout=25,allow_redirects=False)
        print("POST",p,repr(body[:30]),"->",r.status_code,len(r.content),r.headers.get('content-type'),r.content[:120])
    time.sleep(1)
