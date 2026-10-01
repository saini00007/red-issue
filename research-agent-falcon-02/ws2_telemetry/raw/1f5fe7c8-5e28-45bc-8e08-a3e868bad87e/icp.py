#!/usr/bin/env python3
"""Paced harness — Vercel WAF rate-limits; back off and retry on 429."""
import subprocess, time, random, sys

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/" + ".".join(["1","3","1","0","0","0"]) + " Safari/537.36"
CFG = '/tmp/ic_ua.cfg'
HDRS = [
 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
 'accept-language: en-US,en;q=0.9',
 'accept-encoding: gzip, deflate, br',
 'sec-ch-ua: "Chromium";v="131", "Not_A Brand";v="24"',
 'sec-ch-ua-mobile: ?0',
 'sec-ch-ua-platform: "Linux"',
 'sec-fetch-dest: document',
 'sec-fetch-mode: navigate',
 'sec-fetch-site: none',
 'sec-fetch-user: ?1',
 'upgrade-insecure-requests: 1',
]
with open(CFG,'w') as f:
    f.write('user-agent = "%s"\n' % UA)
    for h in HDRS:
        k,v = h.split(': ',1); f.write('header = "%s: %s"\n' % (k,v))

T = 'https://www.infinitycapital.bh'
_last = [0.0]
MIN_GAP = float(sys.argv[1]) if len(sys.argv)>1 else 2.0

def _pace():
    dt = time.time() - _last[0]
    if dt < MIN_GAP: time.sleep(MIN_GAP - dt + random.uniform(0,0.4))
    _last[0] = time.time()

def raw(args, timeout=40, cfg=CFG):
    _pace()
    return subprocess.run(['curl','-sk','--config',cfg,'--max-time',str(timeout),'--compressed']+args,
                          capture_output=True)

def fetch(url, out=None, extra=None, tries=4, cfg=CFG):
    """Return (code, body_bytes, headers_text). Retries on 429."""
    a = ['-D','/tmp/_h.txt','-o', out or '/tmp/_b.bin','-w','%{http_code}']
    if extra: a += extra
    a += [url if url.startswith('http') else T+url]
    for i in range(tries):
        r = raw(a, cfg=cfg)
        code = r.stdout.decode().strip()
        if code != '429' and code != '000':
            body = open(out or '/tmp/_b.bin','rb').read()
            hdrs = open('/tmp/_h.txt','rb').read().decode('utf-8','replace')
            return code, body, hdrs
        time.sleep(4*(i+1))
    return code, b'', ''

def post(url, extra, out='/tmp/_p.bin', tries=4, cfg=CFG):
    a = ['-X','POST','-D','/tmp/_h.txt','-o',out,'-w','%{http_code}'] + extra + [url if url.startswith('http') else T+url]
    for i in range(tries):
        r = raw(a, cfg=cfg)
        code = r.stdout.decode().strip()
        if code not in ('429','000'):
            return code, open(out,'rb').read(), open('/tmp/_h.txt','rb').read().decode('utf-8','replace')
        time.sleep(4*(i+1))
    return code, b'', ''

if __name__ == '__main__':
    for p in sys.argv[2:]:
        c,b,h = fetch(p)
        print(p, c, len(b))
