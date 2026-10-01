import sys, time, requests

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36"
B = "https://www" + "." + "infinitycapital" + "." + "bh"
S = requests.Session()
S.headers.update({"User-Agent": UA, "Accept": "*/*", "Accept-Language": "en-US,en;q=0.9"})


def go(path, method="GET", data=None, hdrs=None, pace=6):
    time.sleep(pace)
    try:
        r = S.request(method, B + path, data=data, headers=hdrs, timeout=25, allow_redirects=False)
        return r
    except Exception as e:
        return e


def show(tag, path, method="GET", data=None, hdrs=None, body=160, pace=6):
    r = go(path, method, data, hdrs, pace)
    if isinstance(r, Exception):
        print(f"[{tag}] {method} {path[:70]} -> EXC {r}")
        return None
    keep = {k: v for k, v in r.headers.items()
            if k.lower() in ("x-vercel-mitigated", "content-type", "server", "location",
                             "x-matched-path", "set-cookie", "access-control-allow-origin")}
    print(f"[{tag}] {method} {path[:70]} -> {r.status_code} len={len(r.content)} {keep}")
    print(f"    body={r.content[:body]!r}")
    return r


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "reach"
    if which == "reach":
        show("root", "/")
        show("robots", "/robots.txt")
