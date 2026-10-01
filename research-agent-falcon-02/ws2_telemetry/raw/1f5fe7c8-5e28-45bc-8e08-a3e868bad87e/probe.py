#!/usr/bin/env python3
import sys, json, urllib.parse, requests
S = requests.Session()
S.verify = False
S.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
import urllib3; urllib3.disable_warnings()

def req(url, **kw):
    try:
        r = S.request(kw.pop('method','GET'), url, timeout=40, allow_redirects=False, **kw)
        return r
    except Exception as e:
        print('ERR', url[:120], e); return None

def show(tag, r):
    if r is None: return
    print(f'--- {tag}: {r.status_code} len={len(r.content)} ct={r.headers.get("content-type")} loc={r.headers.get("location")}')
    return r

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'img':
        u = sys.argv[2]
        r = req(u); show('img', r)
        if r is not None: print(r.content[:200])
    elif cmd == 'line':
        # each line of file: METHOD<TAB>url
        for line in open(sys.argv[2]):
            line=line.strip()
            if not line or line.startswith('#'): continue
            m,u = line.split('\t')
            r = req(u, method=m)
            show(m+' '+u[:90], r)
