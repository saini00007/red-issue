import sys, time, urllib.parse
sys.path.insert(0, ".")
from dp_lib import S, B, go

# _next/image reaches origin (400, not edge-mitigated). Let's confirm origin behavior.
img = "https://images.ctfassets.net/yts1dx0j7jj5/yRvqRHKqEsbLvrma0OXqV/4b64635f8f18ab2e546275054c0f0230/infinity.jpg"
e = urllib.parse.quote(img, safe="")

tests = [
    ("img_no_url", "/_next/image?w=640&q=75"),
    ("img_valid", f"/_next/image?url={e}&w=640&q=75"),
    ("img_w_bad", f"/_next/image?url={e}&w=abc&q=75"),
    ("img_q_bad", f"/_next/image?url={e}&w=640&q=zzz"),
    ("img_lfi", "/_next/image?url=" + urllib.parse.quote("/etc/passwd", safe="") + "&w=640&q=75"),
]
for tag, p in tests:
    r = go(p, pace=8)
    if isinstance(r, Exception):
        print(f"{tag:14} EXC {r}")
        continue
    print(f"{tag:14} {r.status_code} len={len(r.content):6} ct={r.headers.get('content-type','-'):30} "
          f"mp={r.headers.get('x-matched-path','-')[:26]} body={r.content[:80]!r}")
