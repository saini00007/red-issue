import requests, time, sys
B = "https://" + "www.infinity" + "capital" + ".bh"
UAS = {
 "ff": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
 "ch": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
}
def sess(kind="ff"):
    x = requests.Session()
    x.headers.update({
      "User-Agent": UAS[kind],
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language": "en-US,en;q=0.5",
      "Accept-Encoding": "gzip, deflate, br",
      "Connection": "keep-alive",
      "Upgrade-Insecure-Requests": "1",
      "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate",
      "Sec-Fetch-Site": "none", "Sec-Fetch-User": "?1",
    })
    return x
def show(s, p):
    r = s.get(B + p, timeout=30, allow_redirects=False)
    print(r.status_code, len(r.content), r.headers.get("x-vercel-mitigated"), p)
    return r
if __name__ == "__main__":
    for kind in ("ff","ch"):
        s = sess(kind)
        for p in ["/", "/contact", "/404", "/_next/image?w=1080&q=75", "/?id=1&search=test&page=2"]:
            r = show(s, p)
        print("---")
