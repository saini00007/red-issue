import subprocess, time, random, sys

UA_CHROME = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
UA_GBOT = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
BASE = "https://www.infinitycapital.bh"


def fetch(path, method="GET", data=None, hdrs=None, tries=25, ua=UA_CHROME, ctype=None,
          raw=False, timeout=30):
    """Retry past the Vercel bot challenge (403) and rate limit (429/473)."""
    delay = 1.0
    for i in range(tries):
        cmd = ["curl", "-s", "--max-time", str(timeout), "-X", method, "-A", ua,
               "-D", "/tmp/h2.txt", "-o", "/tmp/b2.bin", "-w", "%{http_code}"]
        if data is not None:
            cmd += ["--data-binary", "@-"]
        if ctype:
            cmd += ["-H", "Content-Type: " + ctype]
        for hh in (hdrs or []):
            cmd += ["-H", hh]
        cmd += [BASE + path]
        r = subprocess.run(cmd, input=(data.encode() if isinstance(data, str) else data),
                           capture_output=True)
        code = r.stdout.decode().strip() or "000"
        h = open("/tmp/h2.txt", errors="replace").read()
        b = open("/tmp/b2.bin", "rb").read()
        if code not in ("403", "429", "473", "000"):
            if raw:
                return code, h, b
            return code, h, b
        time.sleep(delay + random.random())
        delay = min(delay * 1.4, 8)
    return code, h, b


if __name__ == "__main__":
    for p in sys.argv[1:]:
        c, h, b = fetch(p)
        print(c, len(b), p)
