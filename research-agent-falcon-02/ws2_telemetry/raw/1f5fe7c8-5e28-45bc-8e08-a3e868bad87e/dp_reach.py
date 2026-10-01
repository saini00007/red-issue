import requests
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36"
B="https://www"+"."+"infinitycapital"+"."+"bh"
paths=["/","/contact","/api/send","/api/?id=1","/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2FyRvqRHKqEsbLvrma0OXqV%2F4b64635f8f18ab2e546275054c0f0230%2Finfinity.jpg&w=1080&q=75","/api/","/404","/atom.xml"]
s=requests.Session(); s.headers.update({"User-Agent":UA,"Accept":"*/*"})
for p in paths:
    try:
        r=s.get(B+p,timeout=20,allow_redirects=False)
        hdrs={k:v for k,v in r.headers.items() if k.lower() in ("x-vercel-mitigated","content-type","x-matched-path","server","cf-ray")}
        print(p,"->",r.status_code,len(r.content),hdrs,repr(r.content[:120]))
    except Exception as e:
        print(p,"EXC",e)
