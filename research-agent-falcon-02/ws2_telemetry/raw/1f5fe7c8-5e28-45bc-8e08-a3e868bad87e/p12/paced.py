import subprocess, time, json, sys, urllib.parse

T = "https://" + "www.infinity" + "capital" + ".bh"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.36"

def req(path, method="GET", data=None, hdrs=None, ctype=None):
    cmd = ["curl", "-s", "-o", "/tmp/p12.bin", "-D", "/tmp/p12.hdr",
           "-w", "%{http_code}|%{size_download}|%{content_type}"]
    for h in (hdrs or []):
        cmd += ["-H", h]
    if ctype:
        cmd += ["-H", "Content-Type: " + ctype]
    if data is not None:
        cmd += ["--data-binary", data]
    cmd += ["-A", UA, "-H", "Accept: */*", "-X", method, T + path]
    subprocess.run(cmd, capture_output=True, text=True)
    hdr = open("/tmp/p12.hdr", errors="replace").read()
    body = open("/tmp/p12.bin", "rb").read()
    code = hdr.splitlines()[0] if hdr else "?"
    mit = "deny" if "x-vercel-mitigated" in hdr else "-"
    return {"status": code, "mit": mit, "len": len(body), "body": body,
            "hdr": hdr, "raw": open("/tmp/p12.bin","rb").read()[:400]}

def show(tag, r, keep=200):
    print(f"[{tag}] {r['status']} mit={r['mit']} len={r['len']} :: {r['raw'][:keep]!r}")
    return r
