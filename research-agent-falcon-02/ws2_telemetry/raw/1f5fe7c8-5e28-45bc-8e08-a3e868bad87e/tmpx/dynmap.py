import subprocess
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
paths=["/","/contact","/about","/services","/insights","/team","/atom.xml","/sitemap.xml","/robots.txt",
"/api/send","/api/contact","/api/","/api?id=1","/api/newsletter","/api/subscribe","/api/search",
"/_next/image","/feeds/all.atom.xml","/404","/admin","/login","/dashboard","/portal","/wp-admin",
"/.env","/.git/config","/api/health","/api/config","/_next/static/chunks/main.js","/graphql","/api/graphql",
"/insights/hello-world","/en/contact","/ar/contact","/api/v1","/careers","/privacy-policy","/terms",
"/api/users","/api/profile","/newsletter","/sitemap-0.xml","/_vercel/insights/view","/api/upload"]
for p in paths:
    r=subprocess.run(["curl","-s","-m","15","-A",UA,"-o","/tmp/p.bin","-D","/tmp/p.hdr",
                      "https://www.infinitycapital.bh"+p],capture_output=True,text=True)
    h=open("/tmp/p.hdr",errors="ignore").read()
    code=h.split("\n")[0].strip()
    def g(k):
        for line in h.split("\n"):
            if line.lower().startswith(k+":"): return line.split(":",1)[1].strip()
        return "-"
    try: n=len(open("/tmp/p.bin","rb").read())
    except: n=-1
    print("%-38s %-18s len=%-7d cache=%-5s matched=%-18s ct=%s"%(
        p,code,n,g("x-vercel-cache"),g("x-matched-path"),g("content-type")[:28]))
