from net import fetch, UA_GBOT
import re, os
os.makedirs("tool_outputs/w2", exist_ok=True)
for p in ["/","/contact","/about","/services","/api/send","/robots.txt","/sitemap.xml","/insights","/api/contact","/api/subscribe","/api/newsletter","/api/preview","/api/webhook","/api/resend","/api/send/"]:
    c,h,b = fetch(p, ua=UA_GBOT, tries=20)
    print("="*70)
    print(p, c, len(b), re.findall(r"x-matched-path: (\S+)", h), re.findall(r"allow: (\S+)", h))
    open("tool_outputs/w2/pg_"+(p.strip("/").replace("/","_") or "root")+".html","wb").write(b)
