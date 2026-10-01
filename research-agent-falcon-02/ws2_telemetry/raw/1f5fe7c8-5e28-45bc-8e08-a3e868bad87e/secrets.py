#!/usr/bin/env python3
import requests, re, time
B="https://www.infinitycapital.bh"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
s=requests.Session(); s.headers.update({"User-Agent":UA})
home=s.get(B+"/",timeout=30).text
chunks=set(re.findall(r'/_next/static/[A-Za-z0-9_./%\-]+\.js', home))
for pg in ["/contact","/about","/investment-philosophy","/investment-portfolio","/privacy-terms"]:
    try:
        h=s.get(B+pg,timeout=30).text
        chunks.update(re.findall(r'/_next/static/[A-Za-z0-9_./%\-]+\.js', h))
    except Exception as e: print("pg err",pg,e)
print("chunks:",len(chunks))
for pg in ["/","/contact"]:
    h=s.get(B+pg,timeout=30).text
    m=re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', h, re.S)
    print(pg,"NEXT_DATA:", (m.group(1)[:1200] if m else "none"))
    for pat in [r'eyJ[A-Za-z0-9_\-]{20,}', r'cf[A-Za-z0-9_\-]{20,}', r're_[A-Za-z0-9_\-]{10,}',
                r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}']:
        for x in list(set(re.findall(pat,h)))[:6]:
            print("   ",pg,"SECRETISH:",x[:80])
    time.sleep(2)
SECPAT = r'(?:[A-Za-z0-9_\-]{20,}\.){1,2}[A-Za-z0-9_\-]{20,}|eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{5,}|re_[A-Za-z0-9_\-]{15,}|sk_[A-Za-z0-9_\-]{15,}'
seen=set()
for u in sorted(chunks):
    try: t=s.get(B+u,timeout=30).text
    except Exception as e: print("err",u,e); continue
    for x in set(re.findall(SECPAT,t)):
        if x not in seen: seen.add(x); print("HIT",u.split('/')[-1],"->",x[:120])
    for kw in ["CONTENTFUL","RESEND","API_KEY","APIKEY","SECRET","TOKEN","password","Authorization","Bearer","accessToken"]:
        i=t.find(kw)
        if i>=0: print(f"  KW {kw} in {u.split('/')[-1]}: ...{t[max(0,i-70):i+130]}...")
    time.sleep(0.5)
print("=== source maps ===")
for u in sorted(chunks)[:5]:
    r=s.get(B+u+".map",timeout=25)
    print(" ",u.split('/')[-1]+".map",r.status_code,len(r.content))
