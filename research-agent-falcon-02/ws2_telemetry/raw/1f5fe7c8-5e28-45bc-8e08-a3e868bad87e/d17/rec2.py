import requests, os, time, json
U = open('/work/ua_final.txt').read().strip()
T = "https://www.infinitycapital.bh"
S = requests.Session()
S.headers.update({'User-Agent': U, 'Accept':'*/*'})

def req(method, path, label=None, hdrs=None, body=None, timeout=30):
    t0=time.time()
    try:
        r = S.request(method, T+path, headers=hdrs or {}, data=body, timeout=timeout, allow_redirects=False)
        dt=time.time()-t0
        loc = r.headers.get('location','')
        xp = r.headers.get('x-matched-path','')
        xv = r.headers.get('x-vercel-mitigated','')
        print("%-46s %s %-7d %5.2fs m=%-22s v=%-30s loc=%s" % (label or (method+" "+path[:40]), r.status_code, len(r.content), dt, xp[:22], xv, loc[:60]))
        return r
    except Exception as e:
        print("%-46s ERR %.1fs %s" % (label or (method+" "+path[:40]), time.time()-t0, e)); return None

print("### Next.js internals")
for p in ["/_next/data/build/contact.json","/_next/static/BUILD_ID","/_next/static/chunks/pages/contact.js",
          "/_next/development/mask-image.svg","/__nextjs_original-stack-frame","/__nextjs_launch-editor",
          "/_next/image?url=%2F%2F&w=640&q=75","/_next/image?url=%2F&w=1&q=1",
          "/_next/static/development/_buildManifest.js","/_next/static/chunks/app/page.js",
          "/server-info","/_next/routes-manifest.json","/api/health","/api/config","/api/healthz"]:
    req("GET", p)

print("\n### RSC / server actions")
RSC={'RSC':'1','Next-Router-Prefetch':'1'}
req("GET","/contact","GET /contact RSC=1",RSC)
req("POST","/contact","POST /contact (RSC action attempt)",{'RSC':'1','Content-Type':'text/x-component;charset=utf-8','Next-Action':'1'},body=b'[]')
req("GET","/","GET / RSC=1",RSC)

print("\n### route / config discovery")
for p in ["/api/send","/api/contact","/api/subscribe","/api/newsletter","/api/webhook","/api/upload",
          "/api/graphql","/graphql","/api/auth","/sitemap.xml","/robots.txt","/.well-known/security.txt",
          "/feed.xml","/feeds/all.atom.xml","/atom.xml","/.env","/.git/config","/next.config.js",
          "/admin","/dashboard","/api/debug","/api/status","/api/v1/send","/api/relay","/api/email"]:
    req("GET", p)

print("\n### static asset / backup probes")
for p in ["/index.html.bak","/package.json","/BUILD_ID","/.vercel/output/static/index.html",
          "/api/send.js","/api/send.mjs","/.DS_Store","/crossdomain.xml","/swagger.json","/openapi.json",
          "/api-docs","/v2/api-docs","/.well-known/openid-configuration"]:
    req("GET", p)
