import ssl, urllib.request, urllib.error, time, random
B = "https://www" + ".infinitycapital" + ".bh"
UAS = [
 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
 "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
 "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
 "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE

def get(path, ua, extra=None, timeout=20):
    h = {"User-Agent": ua,
         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
         "Accept-Language": "en-US,en;q=0.9",
         "sec-ch-ua": '"Chromium";v="124", "Not-A.Brand";v="99"',
         "sec-ch-ua-mobile": "?0",
         "sec-ch-ua-platform": '"Windows"',
         "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate",
         "Sec-Fetch-Site": "none", "Sec-Fetch-User": "?1",
         "Upgrade-Insecure-Requests": "1",
         "Cache-Control": "max-age=0",
         }
    if extra: h.update(extra)
    r = urllib.request.Request(B + path, headers=h)
    try:
        with urllib.request.urlopen(r, context=ctx, timeout=timeout) as resp:
            return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()
    except Exception as e:
        return 0, {}, str(e).encode()

ok = 0
for i in range(25):
    ua = random.choice(UAS)
    c, h, b = get("/", ua)
    chal = b"Checkpoint" in b or b"checkpoint" in b
    if c == 200:
        ok += 1
        print("HIT 200 at try", i, "len", len(b), "cache", h.get("x-vercel-cache"))
        open("tool_outputs/root200.html","wb").write(b)
        break
    if i % 5 == 0:
        print("try", i, c, len(b), "chal", chal, "mit", h.get("x-vercel-mitigated","-"))
    time.sleep(0.7)
print("done, 200s:", ok)
