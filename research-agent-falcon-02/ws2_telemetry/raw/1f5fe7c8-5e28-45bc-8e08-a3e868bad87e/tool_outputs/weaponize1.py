#!/usr/bin/env python3
"""Phase-A weaponization: re-establish origin reachability + capture real HTML."""
import subprocess, sys, os

B = "https://www.infinitycapital.bh"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/" + "1" + "24.0.0.0 Safari/537.36")

TARGETS = [
    ("root",     B + "/"),
    ("about",    B + "/about"),
    ("api",      B + "/api/"),
    ("api_id",   B + "/api/?id=1"),
    ("img",      B + "/_next/image?w=1080&q=75"),
    ("img_url",  B + "/_next/image?url=%2Ffoo&w=640&q=75"),
    ("p404",     B + "/404?q=1"),
    ("atom",     B + "/atom.xml"),
    ("login",    B + "/login"),
    ("private",  B + "/private"),
    ("robots",   B + "/robots.txt"),
    ("sectxt",   B + "/.well-known/security.txt"),
]

os.makedirs("tool_outputs", exist_ok=True)
log = []
for name, url in TARGETS:
    hdr = "tool_outputs/hdr_%s.txt" % name
    bod = "tool_outputs/resp_%s.html" % name
    r = subprocess.run(
        ["curl", "-sk", "-m", "20", "-A", UA,
         "-H", "Accept-Encoding: gzip, deflate",
         "-D", hdr, "-o", bod, "-w", "%{http_code} %{size_download}", url],
        capture_output=True, text=True)
    h = open(hdr, errors="replace").read() if os.path.exists(hdr) else ""
    mit = [l.strip() for l in h.splitlines() if "vercel-mitigated" in l.lower()]
    line = "%-10s %-14s mitigated=%s" % (name, r.stdout.strip(), mit[0] if mit else "NONE")
    log.append(line)
    print(line, flush=True)

open("tool_outputs/weaponize1.log", "w").write("\n".join(log))
