import subprocess, json

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
EP = 'https://www.infinitycapital.bh/api/send'

def post(body, ct, tag):
    cmd = ['curl', '-s', '-k', '-m', '25', '-A', UA, '-X', 'POST', '-D', '/tmp/h_%s.txt' % tag,
           '-o', '/tmp/b_%s.txt' % tag, '-w', 'code=%{http_code} len=%{size_download}', '-H', 'Content-Type: ' + ct,
           '--data-binary', body, EP]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print('== %-22s %s' % (tag, r.stdout))
    b = open('/tmp/b_%s.txt' % tag, 'rb').read()[:300]
    print('   body:', b)
    h = open('/tmp/h_%s.txt' % tag).read()
    for ln in h.splitlines():
        if ln.lower().startswith(('http/', 'x-', 'content-type', 'set-cookie', 'server', 'allow')):
            print('   |', ln)

post('{}', 'application/json', 'json_empty')
post(json.dumps({"name": "probe", "email": "probe@example.org", "message": "d14 test"}), 'application/json', 'json_full')
post('name=probe&email=probe%40example.org&message=d14test', 'application/x-www-form-urlencoded', 'form_full')
post(json.dumps({"targets": ["probe@example.org"], "subject": "d14", "message": "d14"}), 'application/json', 'json_targets')
post('[]', 'application/json', 'json_array')
post('notjson', 'application/json', 'json_bad')
post('<r><x/></r>', 'application/xml', 'xml')
