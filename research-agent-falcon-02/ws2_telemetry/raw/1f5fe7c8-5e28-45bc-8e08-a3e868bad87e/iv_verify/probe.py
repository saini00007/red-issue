#!/usr/bin/env python3
import json, sys, urllib.request, urllib.error

BASE = "https://www.infinitycapital.bh"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/" + "12" + "6.0.0.0 Safari/537.36")


def req(path, method="GET", body=None, extra_headers=None, timeout=30):
    url = path if path.startswith("http") else BASE + path
    data = None
    headers = {
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    if extra_headers:
        headers.update(extra_headers)
    if body is not None:
        if isinstance(body, (dict, list)):
            data = json.dumps(body).encode()
            headers.setdefault("Content-Type", "application/json")
        else:
            data = body.encode() if isinstance(body, str) else body
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, dict(resp.headers), resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode("utf-8", "replace")
    except Exception as e:
        return -1, {}, "EXC: %r" % (e,)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "/"
    method = sys.argv[2] if len(sys.argv) > 2 else "GET"
    body = sys.argv[3] if len(sys.argv) > 3 else None
    b = json.loads(body) if body else None
    st, h, t = req(path, method, b)
    print("STATUS:", st)
    for k in ("content-type", "server", "x-vercel-mitigated", "x-vercel-id", "location", "x-powered-by"):
        if k in h:
            print("HDR %s: %s" % (k, h[k]))
    print("BODY(%d):" % len(t))
    print(t[:3000])
