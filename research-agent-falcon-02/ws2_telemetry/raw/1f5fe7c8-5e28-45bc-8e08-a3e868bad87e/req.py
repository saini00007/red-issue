import sys, requests, json
S = requests.Session()
S.headers.update({
 'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
 'Accept-Language':'en-US,en;q=0.9',
 'Accept-Encoding':'gzip, deflate, br',
 'Upgrade-Insecure-Requests':'1',
 'Sec-Fetch-Dest':'document','Sec-Fetch-Mode':'navigate','Sec-Fetch-Site':'none','Sec-Fetch-User':'?1',
})
B='https://www.infinitycapital.bh'
def go(p, method='GET', **kw):
    try:
        r = S.request(method, B+p, timeout=25, allow_redirects=True, **kw)
        return r
    except Exception as e:
        print('ERR', e); return None
if __name__=='__main__':
    paths = sys.argv[1:] or ['/']
    for p in paths:
        r = go(p)
        if r is None: continue
        print(p, r.status_code, len(r.content), r.headers.get('x-vercel-mitigated'), r.headers.get('content-type'))
