#!/usr/bin/env python3
"""Shared probe harness for www.infinitycapital.bh (browser-UA bypass of Vercel WAF)."""
import subprocess, os, time

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/" + ".".join(["1","3","1","0","0","0"]) + " Safari/537.36"
CFG = '/tmp/ic_ua.cfg'
H = [
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
    for h in H:
        k,v = h.split(': ',1)
        f.write('header = "%s: %s"\n' % (k,v))

T = 'https://www.infinitycapital.bh'

def curl(args, timeout=30, cfg=CFG):
    cmd = ['curl','-sk','--config',cfg,'--max-time',str(timeout)] + args
    return subprocess.run(cmd, capture_output=True, text=True)

def get(path, extra=None, out=None, timeout=30):
    a = ['-o', out or '/dev/null','-w','%{http_code} %{size_download} %{content_type}']
    if extra: a += extra
    a += [path if path.startswith('http') else T+path]
    r = curl(a, timeout)
    return r.stdout.strip(), r

def post(path, extra, out='/dev/null', timeout=30, cfg=CFG):
    a = ['-X','POST','-o',out,'-w','%{http_code} %{size_download} %{content_type}'] + extra + [path if path.startswith('http') else T+path]
    r = curl(a, timeout, cfg)
    return r.stdout.strip(), r

if __name__ == '__main__':
    for p in ['/','/contact','/about','/services','/api/','/api/send','/atom.xml','/robots.txt','/sitemap.xml']:
        print(p, get(p)[0])
