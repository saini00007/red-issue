import re, subprocess, json

BASE = "https://www.infinitycapital.bh"

def get(u, extra=None):
    cmd = ["curl", "-sk", "--max-time", "30", "-w", "\n@@%{http_code}@@%{size_download}"]
    if extra: cmd += extra
    cmd.append(u)
    p = subprocess.run(cmd, capture_output=True)
    return p.stdout

# find buildId
home = get(BASE + "/").decode("utf8", "replace")
m = re.findall(r'"buildId"\s*:\s*"([^"]+)"', home)
print("buildId candidates:", set(m))
bids = set(m) | set(re.findall(r'/_next/static/([A-Za-z0-9_-]{10,})/_(?:build|ssg)Manifest', home))
print("static dir candidates:", bids)

for b in sorted(bids):
    for name in ["_buildManifest.js", "_ssgManifest.js"]:
        u = f"{BASE}/_next/static/{b}/{name}"
        out = get(u)
        code = out.split("@@")[-2] if "@@" in out else "?"
        print("==", u, code, len(out))
        if code == "200":
            body = out.split(b"\n@@")[0].decode("utf8", "replace")
            # print all route-like strings
            routes = set(re.findall(r'"(/[^"]{0,80})"', body)) | set(re.findall(r"'(/[^']{0,80})'", body))
            for r in sorted(routes):
                print("   ", r)
            open(f"tool_outputs/{name}", "w").write(body)
