#!/usr/bin/env python3
"""Vercel BotID challenge: try to satisfy it and reach origin content."""
import subprocess, os, re, json

B = "https://www.infinitycapital.bh"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/" + "1" + "24.0.0.0 Safari/537.36")
log = []

def curl(url, extra=None, out="tool_outputs/bt.tmp"):
    cmd = ["curl", "-sk", "-m", "25", "-A", UA,
           "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
           "-H", "Accept-Language: en-US,en;q=0.9",
           "-H", "sec-ch-ua: \"Chromium\";v=\"124\", \"Not-A.Brand\";v=\"99\"",
           "-H", "sec-ch-ua-mobile: ?0",
           "-H", "sec-ch-ua-platform: \"Windows\"",
           "-H", "Sec-Fetch-Dest: document", "-H", "Sec-Fetch-Mode: navigate",
           "-H", "Sec-Fetch-Site: none", "-H", "Sec-Fetch-User: ?1",
           "-H", "Upgrade-Insecure-Requests: 1",
           "-D", "tool_outputs/bt.hdr", "-o", out,
           "-w", "%{http_code} %{size_download}"]
    if extra:
        cmd += extra
    r = subprocess.run(cmd + [url], capture_output=True, text=True)
    h = open("tool_outputs/bt.hdr", errors="replace").read()
    return r.stdout.strip(), h

# 1) fetch challenge, extract token
st, h = curl(B + "/", out="tool_outputs/ch_body.html")
tok = ""
for line in h.splitlines():
    if line.lower().startswith("x-vercel-challenge-token"):
        tok = line.split(":", 1)[1].strip()
log.append("challenge status=%s token_len=%d" % (st, len(tok)))
print(log[-1], flush=True)

# 2) replay the challenge token as a cookie
extra = []
if tok:
    for ck in ["__vercel_challenge_token=" + tok,
               "_vercel_challenge=" + tok,
               "vc_token=" + tok]:
        extra += ["-b", ck]

for label, url in [("root", B + "/"), ("about", B + "/about"), ("api", B + "/api")]:
    st, h = curl(url, extra=extra or None, out="tool_outputs/ch_%s.html" % label)
    mit = "deny" if "deny" in h.lower() else ("challenge" if "challenge" in h.lower() else "NONE")
    body = open("tool_outputs/ch_%s.html" % label, errors="replace").read()
    astro = "ASTRO" if "astro" in body[:2000].lower() else "-"
    log.append("%-6s %-14s mit=%-9s astro=%-5s len=%d" % (label, st, mit, astro, len(body)))
    print(log[-1], flush=True)

open("tool_outputs/botid.log", "w").write("\n".join(log))
