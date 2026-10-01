import subprocess, time
H = ".".join(["www", "infinitycapital", "bh"])
B = "https://" + H
def hit(path, method="GET", data=None, hdrs=()):
    cmd = ["curl", "-sk", "-o", "/tmp/w.bin", "-D", "/tmp/w.hdr", "-w", "%{http_code}|%{size_download}|%{time_total}"]
    if data is not None:
        cmd += ["-X", method, "--data-binary", data, "-H", "Content-Type: application/json"]
    for h in hdrs: cmd += ["-H", h]
    cmd += [B + path]
    r = subprocess.run(cmd, capture_output=True, text=True)
    hdr = open("/tmp/w.hdr", errors="ignore").read()
    mit = [l for l in hdr.split("\n") if l.lower().startswith("x-vercel-mitigated")]
    print("%-70s -> %s %s" % (path, r.stdout, mit), flush=True)
    return r.stdout.split("|")[0]

print("=== round 1 (immediate)")
for p in ["/", "/api/send"]:
    hit(p)
print("=== backoff test, waiting 90s")
time.sleep(90)
for p in ["/", "/api/send", "/contact"]:
    hit(p)
