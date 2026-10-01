import subprocess, json, sys

BASE = "https://www.infinitycapital.bh"
paths = [
 "/", "/about", "/contact", "/api/", "/404", "/atom.xml", "/feed.xml", "/index.xml",
 "/_next/static/css/32a0546faf171957.css", "/.well-known/security.txt", "/ads.txt",
 "/login", "/admin", "/robots.txt", "/sitemap.xml",
]
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
out = []
for p in paths:
    r = subprocess.run(["curl","-sk","-m","12","-A",UA,"-H","Accept: text/html,*/*",
                        "-o","/tmp/body.out","-D","/tmp/hdr.out","-w","%{http_code} %{size_download}","-L", BASE+p],
                       capture_output=True, text=True)
    body = open("/tmp/body.out","rb").read()[:200]
    hdr = open("/tmp/hdr.out").read()
    mitigated = [l for l in hdr.splitlines() if "vercel-mitigated" in l.lower()]
    line = "%-42s %s  mitigated=%s body=%r" % (p, r.stdout.strip(), mitigated[0].split(":")[1].strip() if mitigated else "none", body[:80])
    print(line, flush=True)
    out.append(line)
open("tool_outputs/phase1_baseline_status.txt","w").write("\n".join(out))
