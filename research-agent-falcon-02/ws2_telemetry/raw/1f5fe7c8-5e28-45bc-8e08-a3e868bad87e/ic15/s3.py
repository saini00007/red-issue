#!/usr/bin/env python3
"""IC15 pass 3: mine the Next.js chunks for the real API contract of /api/send."""
import subprocess, os, re, json
H = "https://www.infinitycapital.bh"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
D = "/tmp/ic15"; os.makedirs(D, exist_ok=True)
W = os.environ["WORK_PATH"]

def get(url, out):
    subprocess.run(["curl","-s","-o",out,"-A",UA,"--max-time","30",url],capture_output=True)
    return os.path.getsize(out) if os.path.exists(out) else 0

# 1. home page -> script srcs
home = D+"/home.html"
get(H+"/?cb=99811", home)
h = open(home, encoding="utf-8", errors="replace").read()
srcs = sorted(set(re.findall(r'src="(/_next/static/[^"]+\.js)"', h)))
print("chunks:", len(srcs))
alljs = ""
for i, s in enumerate(srcs):
    o = f"{D}/c{i}.js"
    get(H+s, o)
    alljs += "\n/*== %s ==*/\n" % s + open(o, encoding="utf-8", errors="replace").read()
open(D+"/all.js","w").write(alljs)
print("total js bytes:", len(alljs))

for kw in ["api/send","resend","targets","subject","from:","to:","reply_to","replyTo","/api/","fetch("]:
    idxs = [m.start() for m in re.finditer(re.escape(kw), alljs)]
    print(f"\n### {kw}: {len(idxs)} hits")
    for j in idxs[:4]:
        print("   ...", alljs[max(0,j-260):j+260].replace("\n"," "))
