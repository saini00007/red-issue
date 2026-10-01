import requests, re, json
B="https://www.infinitycapital.bh"
H={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15"}
r=requests.get(B+"/",headers=H,timeout=30)
h=r.text
print("home",r.status_code,len(h))
m=re.search(r'"buildId":"([^"]+)"',h)
print("buildId:", m.group(1) if m else None)
for pat in [r'_next/static/([^"/]+)/_', r'buildId[^,]{0,40}']:
    print(pat, set(re.findall(pat,h)))
# assets
assets=set(re.findall(r'/_next/static/[^"\']+',h))
print("n_assets",len(assets))
for a in sorted(assets)[:40]: print("  ",a)
open("/work/w53_home.html","w").write(h)
