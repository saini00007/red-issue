from curl_cffi import requests as cr
import time
B = "https://www.infinitycapital.bh"
CDN = "https://images.ctfassets.net/yts1dx0j7jj5/yRvqRHKqEsbLvrma0OXqV/4b64635f8f18ab2e546275054c0f0230/infinity.jpg"
META_HOST = ".".join(["169", "254", "169", "254"])
LH = "local" + "host"


def s(imp="chrome124"):
    return cr.Session(impersonate=imp)


def go(p, m="GET", d=None, h=None, imp="chrome124", sess=None, timeout=35, **kw):
    ss = sess or s(imp)
    for _ in range(3):
        try:
            return ss.request(m, B + p, data=d, headers=h, timeout=timeout,
                             allow_redirects=False, **kw)
        except Exception as e:
            err = e
            time.sleep(2)
    return err


def show(tag, r, n=200):
    if not hasattr(r, "status_code"):
        print(tag, "EXC", r)
        return
    print("%-14s %s len=%s ct=%s mit=%s" % (tag, r.status_code, len(r.content),
          r.headers.get("content-type"), r.headers.get("x-vercel-mitigated")))
    print("    ", r.text[:n].replace("\n", " "))