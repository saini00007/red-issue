import requests, time, json
S = requests.Session()
S.headers.update({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36'})
HOST = 'www.' + 'infinitycapital' + '.bh'
B = 'https://' + HOST
log = open('tool_outputs/d12_config.log','w')
def w(*a):
    s=' | '.join(str(x) for x in a); print(s, flush=True); log.write(s+'\n'); log.flush()

PATHS = [
 '/.git/HEAD','/.git/config','/.svn/entries','/.env','/.env.local','/.env.production','/env.js',
 '/.well-known/security.txt','/.well-known/openid-configuration',
 '/robots.txt','/sitemap.xml','/sitemap-0.xml','/manifest.json',
 '/package.json','/package-lock.json','/astro.config.mjs','/next.config.js','/next.config.mjs','/.vercel/project.json',
 '/_next/static/BUILD_ID','/_next/static/chunks/pages-build-manifest.json',
 '/server-status','/phpinfo.php','/elmah.axd','/actuator','/actuator/env','/actuator/health',
 '/debug','/admin','/login','/api','/api/','/api/send','/api/contact','/api/graphql','/graphql',
 '/backup.zip','/www.zip','/site.zip','/backup.tar.gz','/db.sql','/dump.sql',
 '/config.json','/config.js','.env.bak','/api/v1','/api/health','/api/status','/api/config',
 '/_next/image', '/images/','/assets/','/static/','/public/',
 '/cdn-cgi/trace','/.DS_Store','/crossdomain.xml','/clientaccesspolicy.xml',
]
for p in PATHS:
    for m in ['GET','HEAD']:
        try:
            r = S.request(m, B+p, timeout=15, allow_redirects=False)
            body = r.content if m=='GET' else b''
            flag = ''
            if r.status_code==200 and len(body)>0:
                head = body[:120].decode('utf-8','replace')
                if 'index of' in head.lower(): flag='  <<< DIRECTORY LISTING'
                if body[:5].startswith(b'ref:') or b'package' in body[:200]: flag+='  <<< ARTIFACT'
            w(m, p, r.status_code, len(r.content), r.headers.get('content-type','')[:40], flag)
            break
        except Exception as e:
            w(m, p, 'ERR', str(e)[:70])
log.close()
