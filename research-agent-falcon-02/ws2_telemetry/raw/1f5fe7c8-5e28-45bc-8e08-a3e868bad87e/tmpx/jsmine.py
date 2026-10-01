import subprocess, re, urllib.parse, os
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
os.makedirs("/tmp/js",exist_ok=True)
def get(u, out=None):
    out=out or "/tmp/js/tmp.bin"
    subprocess.run(["curl","-s","-m","25","-A",UA,"-o",out,u],capture_output=True,text=True)
    try: return open(out,"rb").read()
    except: return b""

home=get("https://www.infinitycapital.bh/").decode("utf8","ignore")
scripts=set(re.findall(r'src="([^"]+\.js[^"]*)"',home))
print("scripts found:",len(scripts))
urls=set()
for s in scripts:
    urls.add(urllib.parse.urljoin("https://www.infinitycapital.bh/",s))
# also preload links
for s in set(re.findall(r'href="([^"]*\.js[^"]*)"',home)):
    urls.add(urllib.parse.urljoin("https://www.infinitycapital.bh/",s))
print("resolved:",len(urls))
allsrc=""
for i,u in enumerate(sorted(urls)):
    b=get(u,"/tmp/js/f%d.js"%i)
    allsrc+=b.decode("utf8","ignore")
    print("  %-70s %d bytes"%(u[:70],len(b)))
open("/tmp/js/ALL.js","w").write(allsrc)
print("TOTAL",len(allsrc))

pats = {
 "contentful_space":r'[A-Za-z0-9]{10,24}\s*[,=:]\s*["\'][A-Za-z0-9]{10,24}["\']',
 "cf_delivery_token":r'cfapi[A-Za-z0-9_\-]{10,}',
 "contentful_token_generic":r'(?:CONTENTFUL|SPACE|ACCESS_TOKEN|API_KEY|RESEND|SENDGRID)[A-Z_]*\s*[:=]\s*["\']([^"\']{8,})["\']',
 "resend_key":r're_[A-Za-z0-9]{10,}',
 "aws_key":r'AKIA[0-9A-Z]{16}',
 "jwt":r'eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{5,}',
 "bearer":r'[Bb]earer\s+[A-Za-z0-9_\-\.]{20,}',
 "api_key_long":r'["\']([A-Za-z0-9_\-]{32,})["\']',
 "supabase":r'supabase[a-z0-9]{20,}',
 "firebase":r'AIza[0-9A-Za-z_\-]{35}',
}
for name,p in pats.items():
    m=re.findall(p,allsrc)
    m=[x if isinstance(x,str) else x[0] for x in m]
    m=list(dict.fromkeys([x for x in m if x]))
    print("\n%-24s hits=%d"%(name,len(m)))
    for x in m[:12]: print("    ",x[:90])

# contentful space id / env exposure in the raw HTML too
print("\n### in HTML inline scripts")
for p in [r'contentful',r'ctfassets',r'resend',r'api[_-]?key',r'token']:
    for mm in re.finditer(p,home,re.I):
        s=max(0,mm.start()-120); print("  ...",home[s:mm.start()+160].replace("\n"," ")[:260])
        break
