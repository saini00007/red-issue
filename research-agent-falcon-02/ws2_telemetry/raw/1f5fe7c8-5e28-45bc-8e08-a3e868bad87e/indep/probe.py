import requests, time, sys

B = "https://www.infinitycapital.bh"
UAS = [
 "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
 "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
 "Mozilla/5.0 (X11; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0",
 "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36",
 "Googlebot/2.1 (+http://www.google.com/bot.html)",
]

def try_get(ua, extra=None, url="/contact"):
    h = {"User-Agent": ua, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
         "Accept-Language": "en-US,en;q=0.9"}
    if extra: h.update(extra)
    try:
        r = requests.get(B+url, headers=h, timeout=25)
    except Exception as e:
        return None, str(e)
    return r, None

for i, ua in enumerate(UAS):
    r, e = try_get(ua)
    if e:
        print(i, "ERR", e); continue
    print(i, r.status_code, len(r.content), r.headers.get("x-vercel-mitigated"), r.headers.get("x-matched-path"), repr(r.text[:60]))
    time.sleep(1)
