#!/usr/bin/env python3
"""W19: independent boolean/time differential test for claimed SQLi cells."""
import hashlib, sys, time, urllib.request, urllib.error, json

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
BASE = "https://www.infinitycapital.bh"

def get(url, timeout=25, extra=None):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    if extra:
        req.add_header(*extra)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
            return r.status, dict(r.headers), body, time.time() - t0
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read(), time.time() - t0
    except Exception as e:
        return 0, {}, str(e).encode(), time.time() - t0

def norm(b):
    # strip volatile bits (vite hashes, csrf tokens, dates)
    import re
    s = b.decode("utf-8", "replace")
    s = re.sub(r"\d{10,}", "NUM", s)
    s = re.sub(r"<!--[\s\S]*?-->", "", s)
    return hashlib.md5(s.encode()).hexdigest()

def pair(path, param, tpl):
    """tpl must contain {v} for the injected value"""
    a = BASE + path.replace("{v}", tpl.format(v="1"))
    b = BASE + path.replace("{v}", tpl.format(v="2"))
    res = {}
    for k, u in (("T", a), ("F", b)):
        st, h, body, dt = get(u)
        res[k] = (st, len(body), norm(body), round(dt, 2), h.get("x-vercel-mitigated", ""))
    same = res["T"][2] == res["F"][2] and res["T"][1] == res["F"][1]
    print(f"{path} [{param}] T={res['T']} F={res['F']} -> {'SAME (no oracle)' if same else 'DIFFERENTIAL'}")
    return same, res

if __name__ == "__main__":
    tests = [
        ("/?page={v}", "page", "{v}"),
        ("/?id={v}", "id", "{v}"),
        ("/api/?id={v}", "id", "{v}"),
        ("/contact?cb={v}", "cb", "{v}"),
        ("/contact?q={v}", "q", "{v}"),
        ("/?search={v}", "search", "{v}"),
    ]
    summary = {}
    for path, param, tpl in tests:
        try:
            same, res = pair(path, param, tpl)
            summary[path] = {"differential": not same, "detail": {k: list(v) for k, v in res.items()}}
        except Exception as e:
            print(path, "ERR", e)
    json.dump(summary, open("w19_diff.json", "w"), indent=1)
