#!/usr/bin/env python3
"""Follow redirects on the origin-reachable paths and dump real content."""
import subprocess, os

B = "https://www.infinitycapital.bh"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/" + "1" + "24.0.0.0 Safari/537.36")

CASES = [
    ("api_follow",     B + "/api/"),
    ("api_id_follow",  B + "/api/?id=1"),
    ("img_url_follow", B + "/_next/image?url=%2Ffoo&w=640&q=75"),
    ("p404",           B + "/404?q=1"),
    ("p404_mk",        B + "/404?q=ICMARKER9"),
    ("img_mk",         B + "/_next/image?url=ICMARKER9&w=640&q=75"),
    ("api_mk",         B + "/api/?id=ICMARKER9"),
    ("root_follow",    B + "/"),
]

os.makedirs("tool_outputs", exist_ok=True)
log = []
for name, url in CASES:
    hdr = "tool_outputs/f_%s.hdr" % name
    bod = "tool_outputs/f_%s.body" % name
    r = subprocess.run(
        ["curl", "-skL", "-m", "25", "-A", UA,
         "-D", hdr, "-o", bod,
         "-w", "%{http_code} %{size_download} %{url_effective}", url],
        capture_output=True, text=True)
    h = open(hdr, errors="replace").read() if os.path.exists(hdr) else ""
    mit = "deny" if "vercel-mitigated: deny" in h.lower() else "NONE"
    body = open(bod, errors="replace").read() if os.path.exists(bod) else ""
    reflected = "REFLECTED" if "ICMARKER9" in body else "no"
    line = "%-14s %-22s mit=%-4s refl=%-9s body=%r" % (
        name, r.stdout.strip()[:22], mit, reflected, body[:90])
    log.append(line)
    print(line, flush=True)

open("tool_outputs/follow.log", "w").write("\n".join(log))
