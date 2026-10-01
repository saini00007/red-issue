import ssl, urllib.request, urllib.error, json, time

BASE = "https://www.infinitycapital.bh"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36"
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE

def req(path, method="GET", data=None, ctype="application/json", hdrs=None):
    h = {"User-Agent": UA, "Accept": "*/*"}
    if ctype: h["Content-Type"] = ctype
    if hdrs: h.update(hdrs)
    body = data.encode() if isinstance(data, str) else (json.dumps(data).encode() if data is not None else None)
    r = urllib.request.Request(BASE + path, data=body, headers=h, method=method)
    try:
        resp = urllib.request.urlopen(r, timeout=25, context=ctx)
        return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()
    except Exception as e:
        return "ERR", {}, str(e).encode()

def p(tag, path, method="GET", **kw):
    s, h, b = req(path, method, **kw)
    loc = h.get("Location") or h.get("location") or "-"
    print(f"[{tag}] {method} {path} -> {s} len={len(b)} loc={loc} srv={h.get('server','-')} mit={h.get('x-vercel-mitigated','-')}")
    if len(b) and len(b) < 600:
        print("      body:", b.decode('utf-8','replace')[:400].replace("\n"," "))

p("root", "/")
p("api-root", "/api/")
p("api-contact-GET", "/api/contact")
p("api-contact-POST", "/api/contact", "POST", data={})
p("api-send-GET", "/api/send")
p("api-send-OPTIONS", "/api/send", "OPTIONS")
p("atom", "/atom.xml")
p("feeds", "/feeds/all.atom.xml")
p("sitemap", "/sitemap.xml")
p("robots", "/robots.txt")
p("login", "/login")
p("admin", "/admin")
p("dash", "/dashboard")
