import json, sys, time
sys.path.insert(0, ".")
from dp_lib import S, B, go

tag = sys.argv[1]

def rpt(r, body=200):
    if isinstance(r, Exception):
        print(f"[{tag}] EXC {r}")
        return
    keep = {k: v for k, v in r.headers.items()
            if k.lower() in ("x-vercel-mitigated", "content-type", "server", "location",
                             "x-matched-path", "x-nextjs-cache", "cache-control", "age", "etag")}
    print(f"[{tag}] {r.status_code} len={len(r.content)} {json.dumps(keep)}")
    print(f"    {r.content[:body]!r}")


if tag == "send":
    # Re-validate the claimed open email relay. Marker-only, to OUR OWN address pattern.
    body = json.dumps({"name": "vapt-probe", "email": "probe@invalid.example",
                       "subject": "probe-subject", "message": "vapt-marker-9f21",
                       "targets": ["probe@invalid.example"]})
    rpt(go("/api/send", "POST", body,
           {"Content-Type": "application/json"}, pace=14))

elif tag == "send_form":
    rpt(go("/api/send", "POST",
           "name=vapt&email=probe@invalid.example&subject=s&message=vapt-marker-9f21&targets=probe@invalid.example",
           {"Content-Type": "application/x-www-form-urlencoded"}, pace=14))

elif tag == "send_multipart":
    rpt(go("/api/send", "POST", None, {"_method": "POST"}, pace=0))

elif tag == "contact_post":
    body = json.dumps({"name": "vapt-probe", "email": "probe@invalid.example",
                       "message": "vapt-marker-9f21"})
    rpt(go("/api/contact", "POST", body, {"Content-Type": "application/json"}, pace=14))

elif tag == "secrets":
    rpt(go("/.env", pace=12))
    rpt(go("/.git/HEAD", pace=12))
    rpt(go("/.git/config", pace=12))
    rpt(go("/package.json", pace=12))
    rpt(go("/api/", pace=12))

elif tag == "static":
    rpt(go("/_next/static/chunks/webpack.js", pace=12), body=120)
    rpt(go("/sitemap.xml", pace=12), body=300)

elif tag == "srcmap":
    rpt(go("/_next/static/chunks/main-app.js.map", pace=12), body=80)
    rpt(go("/opengraph-image", pace=12), body=80)

elif tag == "err":
    # error handling / verbose errors -> info leak
    rpt(go("/_next/image?url=%00%ff%fe&w=640&q=75", pace=12))
    rpt(go("/%ff%fe", pace=12))
    rpt(go("/api/send%00.json", pace=12))
