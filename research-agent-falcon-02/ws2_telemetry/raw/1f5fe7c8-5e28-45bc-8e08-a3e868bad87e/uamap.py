import requests
B = "https://" + "www.infinity" + "capital" + ".bh"
UAS = {
 "python-requests": None,
 "sqlmap": "sqlmap/1.10.8#stable (https://sqlmap.org)",
 "chrome125": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36",
 "empty": "",
 "curl": "curl/8.5.0",
 "safari": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
 "wget": "Wget/1.21",
 "python-urllib": "Python-urllib/3.11",
 "go-http": "Go-http-client/1.1",
}
for name, ua in UAS.items():
    h = {}
    if ua is not None:
        h["User-Agent"] = ua
    try:
        r = requests.get(B + "/", headers=h, timeout=25)
        print(f"{name:18} {r.status_code} len={len(r.content)} mit={r.headers.get('x-vercel-mitigated','-')}")
    except Exception as e:
        print(name, "EXC", repr(e)[:100])
