#!/usr/bin/env python3
"""Retry-until-real-response helper: Vercel checkpoint returns 403 randomly;
keep retrying until we get a genuine app response (non-challenge)."""
import subprocess, time, sys, hashlib

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def fetch(url, method="GET", data=None, headers=None, tries=25, want=200):
    hdrs = ["-A", UA]
    if headers:
        for k, v in headers.items():
            hdrs += ["-H", f"{k}: {v}"]
    last = None
    for i in range(tries):
        cmd = ["curl", "-sk", "--max-time", "25", "-o", "/tmp/_b", "-w", "%{http_code}"]
        if method != "GET":
            cmd += ["-X", method]
        if data:
            cmd += ["--data-binary", "@/tmp/_d"] if isinstance(data, str) else []
        cmd += hdrs + [url]
        if isinstance(data, bytes):
            open("/tmp/_d", "wb").write(data)
        r = subprocess.run(cmd, capture_output=True, text=True)
        code = r.stdout.strip()
        body = open("/tmp/_b", "rb").read()
        last = (code, body)
        challenge = b"Vercel Security Checkpoint" in body[:4000]
        if code == str(want) and not challenge:
            return code, body, i + 1
        time.sleep(0.8)
    return last[0], last[1], -1

if __name__ == "__main__":
    url = sys.argv[1]
    c, b, t = fetch(url)
    print(f"code={c} tries={t} len={len(b)} md5={hashlib.md5(b).hexdigest()[:12]}")
    sys.stdout.write(b[:600].decode("utf-8", "replace"))
