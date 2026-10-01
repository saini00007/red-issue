import urllib.request, urllib.parse, time, json, sys

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
URL = 'https://www.infinitycapital.bh/api/send'
BASE = dict(fname='Test', lname='User', areacode='+973', tel='12345678',
            cname='probeuser', subject='Investment Opportunities',
            msg='hello test message', check='on',
            targets='info@infinitycapital.bh')


def post(fields=None, ctype='application/x-www-form-urlencoded', raw=None, hdrs=None, method='POST'):
    data = raw if raw is not None else (urllib.parse.urlencode(fields).encode() if ctype.startswith('application/x-www') else fields)
    h = {'User-Agent': UA, 'Content-Type': ctype, 'Accept': 'application/json',
         'Referer': 'https://www.infinitycapital.bh/contact'}
    if hdrs:
        h.update(hdrs)
    r = urllib.request.Request(URL, data=data, headers=h, method=method)
    for _ in range(5):
        try:
            resp = urllib.request.urlopen(r, timeout=50)
            return resp.status, resp.read()[:800].decode('utf8', 'ignore')
        except Exception as e:
            code = getattr(e, 'code', None)
            if code == 429:
                time.sleep(10); continue
            try:
                return code, e.read()[:800].decode('utf8', 'ignore')
            except Exception:
                return 'ERR', str(e)[:200]
    return 429, 'ratelimited'


def multipart(fields):
    boundary = '----IC' + 'abc123'
    parts = []
    for k, v in fields.items():
        parts.append(('--%s\r\nContent-Disposition: form-data; name="%s"\r\n\r\n%s\r\n' % (boundary, k, v)).encode())
    parts.append(('--%s--\r\n' % boundary).encode())
    return b''.join(parts), 'multipart/form-data; boundary=%s' % boundary
