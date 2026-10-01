import subprocess, re, json
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
def get(u,extra=None):
    c=["curl","-s","-m","25,".strip(),"-A",UA,"-D","/tmp/h.hdr"]
    for h in (extra or []): c+=["-H",h]
    c+=["-o","/tmp/h.bin",u]
    subprocess.run(c,capture_output=True,text=True)
    return open("/tmp/h.bin","rb").read().decode("utf8","ignore")

home=get("https://www.infinitycapital.bh/")
open("/tmp/home.html","w").write(home)
print("home len",len(home))

print("### env/token leakage in server-rendered flight payload")
pats={
 "NEXT_PUBLIC_":r'NEXT_PUBLIC_[A-Z_]+',
 "SPACE_ID":r'"spaceId":"[^"]+"',
 "ACCESS_TOKEN":r'"accessToken":"[^"]+"',
 "cdnToken":r'images\.ctfassets\.net/[^"\'\\ ]{0,40}',
 "env assignment":r'(?:RESEND|CONTENTFUL|MAPI|INTERNAL|ADMIN|SECRET|PASSWORD|KEY)[A-Z_]*["\']?\s*[:=]\s*["\'][^"\']{6,}["\']',
 "bearer/jwt":r'eyJ[A-Za-z0-9_\-]{10,}\.',
 "any 24+ char b64ish in inline script":r'"[A-Za-z0-9_\-]{40,}"',
}
for n,p in pats.items():
    m=re.findall(p,home)
    m=list(dict.fromkeys([x if isinstance(x,str) else x[0] for x in m]))
    print(" %-34s %d  %s"%(n,len(m),m[:4]))

print("\n### RSC flight request (Next.js server data) - does it leak more?")
rsc=get("https://www.infinitycapital.bh/",["RSC: 1","Next-Router-State-Tree: %5B%22%22%5D"])
print("rsc len",len(rsc))
for n,p in [("token",r'"accessToken":"[^"]+"'),("env",r'NEXT_PUBLIC_[A-Z_]+'),("secret",r'(RESEND|CONTENTFUL|SECRET|KEY)[A-Z_]*["\']?\s*[:=]\s*["\'][^"\']{6,}')]:
    print("  rsc %-8s %s"%(n,re.findall(p,rsc)[:4]))

print("\n### Build manifest / buildId + non-exposed files")
for p in ["/_next/static/<BUILDID>/_buildManifest.js"]:
    pass
bm=re.findall(r'"buildId":"([^"]+)"',home)
print(" buildId:",bm)
if bm:
    for u in ["/_next/static/%s/_buildManifest.js"%bm[0], "/_next/static/%s/_ssgManifest.js"%bm[0]]:
        b=get("https://www.infinitycapital.bh"+u)
        print("  %-55s len=%d"%(u[:55],len(b)))
        for n,pp in [("token",r'"accessToken":"[^"]+"'),("env",r'NEXT_PUBLIC_[A-Z_]+')]:
            print("     ",n,re.findall(pp,b)[:3])

print("\n### source maps exposed?")
import random
m=re.findall(r'/_next/static/chunks/[a-zA-Z0-9\-_/\.]+\.js',home)
print(" sample chunk",m[:3])
for mm in m[:6]:
    b=get("https://www.infinitycapital.bh"+mm+".map")
    print("  %-60s map_len=%d"%(mm[:60],len(b)))
