import urllib.request, urllib.parse, json
BASE="https://www.infinitycapital.bh/api/send"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
def post(raw):
    req=urllib.request.Request(BASE,data=raw.encode(),headers={"User-Agent":UA,"Content-Type":"application/x-www-form-urlencoded","Accept":"*/*"})
    try:
        r=urllib.request.urlopen(req,timeout=40); return r.status, r.read()[:500]
    except Exception as e:
        try: b=e.read()[:500]
        except: b=b""
        return getattr(e,'code',0), b

# discover the real recipient field name
cands=["to","email","recipient","rcpt","target","to_email","t_o","dest","mailto"]
for c in cands:
    body=f"fname=T&lname=U&areacode=973&tel=5551234&cname=C&subject=S&msg=M&check=on&{c}=probe@www.infinitycapital.bh"
    st,b=post(body)
    print(f"{c}: {st} {b[:160]!r}")
print("--- json ---")
for j in ['{"to":"probe@www.infinitycapital.bh","msg":"hi"}',
          '{"email":"probe@www.infinitycapital.bh","subject":"s","message":"m"}']:
    req=urllib.request.Request(BASE,data=j.encode(),headers={"User-Agent":UA,"Content-Type":"application/json"})
    try:
        r=urllib.request.urlopen(req,timeout=40); print(j, r.status, r.read()[:300])
    except Exception as e:
        try: print(j, e.code, e.read()[:300])
        except: print(j, e)