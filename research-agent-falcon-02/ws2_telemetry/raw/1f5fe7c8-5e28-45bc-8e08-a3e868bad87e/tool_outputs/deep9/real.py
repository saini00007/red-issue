#!/usr/bin/env python3
"""deep9: Vercel checkpoint is probabilistic -> retry until a REAL origin response
(non-403) is obtained. Dumps body+headers to evidence dir."""
import subprocess, sys, os, time, json, hashlib

OUT = os.environ.get("DEEP9_OUT", os.path.dirname(os.path.abspath(__file__)))
os.makedirs(OUT, exist_ok=True)
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
BASE = "https://www.infinitycapital.bh"

def fetch(path, method="GET", data=None, ctype="application/json", tries=25, sleep=0.6, hdrs=None):
    """returns (status, body, headers) of a real (non-challenge) response or (None,None,None)"""
    url = path if path.startswith("http") else BASE + path
    for i in range(tries):
        cmd = ["curl", "-s", "-m", "25", "-A", UA,
               "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
               "-H", "Accept-Language: en-US,en;q=0.9",
               "-D", "-", "-o", "-", "-w", "\n@@STATUS:%{http_code}\n"]
        if method != "GET":
            cmd += ["-X", method]
            if data is not None:
                cmd += ["-H", "Content-Type: " + ctype, "--data-binary", data]
        for h in (hdrs or []):
            cmd += ["-H", h]
        cmd.append(url)
        try:
            p = subprocess.run(cmd, capture_output=True, timeout=40)
            out = p.stdout
        except Exception:
            continue
        try:
            raw, st = out.rsplit(b"\n@@STATUS:", 1)
            status = st.strip().decode()
        except ValueError:
            continue
        head, _, body = raw.partition(b"\r\n\r\n")
        if status == "403" and b"Vercel Security Checkpoint" in body:
            time.sleep(sleep); continue
        return status, body, head.decode(errors="replace")
    return None, None, None

def save(name, body):
    if body is None: return
    p = os.path.join(OUT, name)
    open(p, "wb").write(body)
    return p

if __name__ == "__main__":
    path = sys.argv[1]
    method = sys.argv[2] if len(sys.argv) > 2 else "GET"
    data = sys.argv[3] if len(sys.argv) > 3 else None
    st, body, head = fetch(path, method, data)
    print("STATUS:", st)
    if head: print(head[:1500])
    if body: print("BODYLEN", len(body), "MD5", hashlib.md5(body).hexdigest()); print(body[:800])
