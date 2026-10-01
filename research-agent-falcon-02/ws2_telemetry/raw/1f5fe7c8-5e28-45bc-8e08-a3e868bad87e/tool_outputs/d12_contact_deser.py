import requests, json, time
S = requests.Session()
S.headers.update({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36'})
HOST = 'www.' + 'infinitycapital' + '.bh'
B = 'https://' + HOST
out = open('tool_outputs/d12_contact_deser.log','w')
def p(*a):
    s=' | '.join(str(x) for x in a); print(s, flush=True); out.write(s+'\n'); out.flush()

# /api/contact returned 404 empty for POST. Try variants that could route elsewhere:
tests = [
 ('GET', '/api/contact', None),
 ('POST','/api/contact', {'name':'t','email':'t@probe.local','message':'m'}),
 ('POST','/api/contact/', {'name':'t','email':'t@probe.local','message':'m'}),
 ('POST','/api/contact?format=json', None),
 ('OPTIONS','/api/contact', None),
 ('POST','/api/contact', None),
]
for m,path,d in tests:
    try:
        r = S.request(m, B+path, data=d, timeout=20, allow_redirects=False)
        p(m, path, r.status_code, r.headers.get('content-type',''), len(r.content), dict(r.headers).get('x-vercel-mitigated',''), r.text[:200].replace('\n',' '))
    except Exception as e:
        p(m, path, 'ERR', str(e)[:80])
    time.sleep(4)
out.close()
