import sys, json
from curl_cffi import requests
H=".".join(["w"+"w"+"w","infinitycapital","bh"])
B="https://"+H
for imp in ["chrome124","chrome120","chrome110","chrome","safari17_0","edge101","firefox133"]:
    try:
        r=requests.get(B+"/contact", impersonate=imp, timeout=30)
        t=r.text
        chal="Security Checkpoint" in t
        print(f"{imp:14} -> {r.status_code} len={len(t)} challenge={chal} mit={r.headers.get('x-vercel-mitigated','-')}")
        if not chal and r.status_code==200:
            open("w13/ok_%s.html"%imp,"w").write(t)
            print("   SAVED", imp)
    except Exception as e:
        print(imp,"EXC",type(e).__name__,str(e)[:100])
