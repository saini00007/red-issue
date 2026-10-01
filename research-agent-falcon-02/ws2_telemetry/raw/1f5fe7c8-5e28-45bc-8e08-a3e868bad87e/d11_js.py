import sys, re, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from R import req, T

os.makedirs("/tmp/w11/js", exist_ok=True)
CHUNKS = """/_next/static/chunks/webpack-e401313d27ef7f61.js
/_next/static/chunks/117-4ba60eb06d2ce296.js
/_next/static/chunks/275-ea7b562607231006.js
/_next/static/chunks/341-553bcb827a52d4aa.js
/_next/static/chunks/489-c3a66469350d58bd.js
/_next/static/chunks/71-fbecd7aa70f9e321.js
/_next/static/chunks/711-90c81a42d9859d8d.js
/_next/static/chunks/743-7f9d0b5cebfd0486.js
/_next/static/chunks/app/%5Bslug%5D/page-b4cf0ec49dd0c737.js
/_next/static/chunks/app/%5Bslug%5D/template-0dafb77d99dbfc0f.js
/_next/static/chunks/app/layout-2aac163e3ced1001.js
/_next/static/chunks/app/page-85182612bc0d92d0.js
/_next/static/chunks/fd9d1056-3902e23722a6b2db.js
/_next/static/chunks/main-app-2dcde4753ea0d175.js""".split()

alljs = ""
for c in CHUNKS:
    r = req("GET", c)
    if r.status_code == 200:
        name = c.rsplit("/", 1)[-1].replace("%5B", "").replace("%5D", "")
        open("/tmp/w11/js/" + name, "w").write(r.text)
        alljs += "\n/* %s */\n" % c + r.text
    else:
        print("skip", c, r.status_code)
open("/tmp/w11/all.js", "w").write(alljs)
print("total js bytes", len(alljs))

print("\n=== env / secrets ===")
for pat in [r'NEXT_PUBLIC_[A-Z_]+', r'[A-Z_]{3,}(?:KEY|SECRET|TOKEN|PASSWORD|DSN)', r'https?://[a-zA-Z0-9._-]+\.(?:supabase|firebase|mongodb|onrender|upstash)[a-zA-Z0-9._/-]*',
            r'eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}', r'sk_live[a-zA-Z0-9]+', r'AIza[0-9A-Za-z_-]{30,}']:
    m = sorted(set(re.findall(pat, alljs)))
    if m:
        print(pat, "->", m[:8])

print("\n=== api routes ===")
for p in sorted(set(re.findall(r'["\'`](/api/[a-zA-Z0-9/_-]*)', alljs))):
    print("  ", p)

print("\n=== other in-scope paths ===")
for p in sorted(set(re.findall(r'["\'`](/(?!_next|api)[a-zA-Z0-9][a-zA-Z0-9/_-]{2,40})["\'`]', alljs)))[:60]:
    print("  ", p)
