#!/usr/bin/env python3
"""w14: full-browser-header HTTP helper + differential SQLi/NoSQLi/CMDi oracle
against www.infinitycapital.bh (Vercel BotID challenge aware)."""
import sys, time, json, hashlib, requests, urllib3
urllib3.disable_warnings()

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
HDRS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "sec-ch-ua": '"Chromium";v="131", "Google Chrome";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
}
S = requests.Session()
S.headers.update(HDRS)

DELAY = float(sys.argv[1]) if len(sys.argv) > 1 else 2.0


def fetch(url, method="GET", data=None, headers=None, timeout=25):
    time.sleep(DELAY)
    h = dict(headers or {})
    try:
        r = S.request(method, url, data=data, headers=h, timeout=timeout,
                       allow_redirects=True, verify=False)
    except Exception as e:
        return {"code": -1, "err": str(e), "len": 0, "h": {}, "body": "", "t": 0.0}
    body = r.text
    return {
        "code": r.status_code,
        "len": len(body),
        "h": {k.lower(): v for k, v in r.headers.items()},
        "body": body,
        "sha": hashlib.sha256(body.encode(errors="ignore")).hexdigest()[:12],
        "t": r.elapsed.total_seconds(),
        "mitigated": r.headers.get("x-vercel-mitigated", ""),
    }


def show(tag, r):
    print(f"{tag:<44} code={r['code']} len={r['len']} t={r['t']:.2f} "
          f"mit={r.get('mitigated','-')} sha={r.get('sha','-')}")


if __name__ == "__main__":
    B = "https://www.infinitycapital.bh"
    for u in sys.argv[2:] or ["/contact?cb=1&q=test"]:
        r = fetch(B + u)
        show(u, r)
