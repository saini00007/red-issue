import requests
T = "https://" + "www.infinitycapital" + ".bh"
paths = ["/", "/contact", "/_next/image?url=x", "/api/", "/atom.xml", "/sitemap.xml",
         "/robots.txt", "/about", "/feeds/all.atom.xml", "/api/contact", "/api/send"]
for p in paths:
    try:
        r = requests.get(T + p, timeout=20, allow_redirects=False)
        mit = r.headers.get("x-vercel-mitigated", "-")
        srv = r.headers.get("server", "-")
        print(f"{p:24} {r.status_code} len={len(r.content):7} mit={mit} srv={srv}")
    except Exception as e:
        print(p, "EXC", e)
