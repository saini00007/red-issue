#!/usr/bin/env python3
"""w14 fetch helper — replays requests through a solved _vcrcs Vercel challenge cookie."""
import os, json, time, hashlib, sys, requests, urllib3
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
}
BASE = "https://www.infinitycapital.bh"
COOKIE_FILE = os.environ.get("W14_COOKIES", "/work/cookies.json")


def load_cookies():
    if not os.path.exists(COOKIE_FILE):
        return {}
    try:
        cs = json.load(open(COOKIE_FILE))
        return {c["name"]: c["value"] for c in cs}
    except Exception:
        return {}


S = requests.Session()
S.headers.update(HDRS)
S.cookies.update(load_cookies())
DELAY = float(os.environ.get("W14_DELAY", "1.5"))


def fetch(path, method="GET", data=None, headers=None, timeout=25, base=BASE):
    time.sleep(DELAY)
    url = path if path.startswith("http") else base + path
    try:
        r = S.request(method, url, data=data, headers=headers or {},
                       timeout=timeout, allow_redirects=True, verify=False)
    except Exception as e:
        return {"code": -1, "len": 0, "h": {}, "body": "", "err": str(e), "t": 0.0}
    b = r.text
    return {"code": r.status_code, "len": len(b), "h": {k.lower(): v for k, v in r.headers.items()},
            "body": b, "sha": hashlib.sha256(b.encode(errors="ignore")).hexdigest()[:12],
            "t": r.elapsed.total_seconds(), "mitigated": r.headers.get("x-vercel-mitigated", ""),
            "url": r.url}


def show(tag, r):
    print(f"{tag:<46} code={r['code']} len={r['len']:>7} t={r['t']:.2f} "
          f"mit={r.get('mitigated') or '-'} sha={r.get('sha','-')}")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        show(p, fetch(p))
