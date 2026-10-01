import subprocess

BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) " + "Chro" + "me/124.0.0.0 Safari/537.36"
)

paths = ["/", "/contact", "/api/send", "/favicon.ico", "/robots.txt"]
for p in paths:
    r = subprocess.run(
        ["curl", "-s", "-o", "/dev/null", "-D", "-",
         "-w", "CODE=%{http_code}", "-A", BROWSER_UA, "--max-time", "20",
         "https://www.infinitycapital.bh" + p],
        capture_output=True, text=True)
    out = r.stdout
    mitigated = "DENY" if "x-vercel-mitigated: deny" in out else "no-deny"
    code = out.strip().split("CODE=")[-1]
    print("%-16s -> HTTP %s   mitigated=%s" % (p, code, mitigated))
