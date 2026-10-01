import requests,time
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
for p,m in [("/","GET"),("/contact","GET"),("/api/send","POST")]:
    r=requests.request(m,"https://www.infinitycapital.bh"+p,headers={"User-Agent":UA},timeout=25,allow_redirects=False)
    print(p,r.status_code,len(r.content),r.headers.get("x-vercel-mitigated"))
    time.sleep(2)
