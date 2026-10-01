import subprocess, time, random, sys, os, json
BASE = "https://www.infinitycapital.bh"
UAS = [
 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
 "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
 "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
 "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
 "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
]
HDRS = [
 ["Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
  "Accept-Language: en-US,en;q=0.9", "Upgrade-Insecure-Requests: 1",
  "Sec-Fetch-Dest: document","Sec-Fetch-Mode: navigate","Sec-Fetch-Site: none","Sec-Fetch-User: ?1"],
 ["Accept: */*", "Accept-Language: en-US,en;q=0.9"],
]

def once(path, method="GET", data=None, hdrs=None, ctype=None, timeout=30, extra=None):
    cmd = ["curl","-s","--max-time",str(timeout),"-X",method,"-A",random.choice(UAS),
           "--compressed","-D","/tmp/d13h.txt","-o","/tmp/d13b.bin","-w","%{http_code}"]
    if data is not None: cmd += ["--data-binary","@-"]
    if ctype: cmd += ["-H","Content-Type: "+ctype]
    for hh in (extra if extra is not None else random.choice(HDRS)): cmd += ["-H",hh]
    for hh in (hdrs or []): cmd += ["-H",hh]
    cmd += [BASE+path]
    r = subprocess.run(cmd, input=(data.encode() if isinstance(data,str) else data), capture_output=True)
    code = r.stdout.decode().strip() or "000"
    try: h = open("/tmp/d13h.txt",errors="replace").read()
    except: h=""
    try: b = open("/tmp/d13b.bin","rb").read()
    except: b=b""
    return code,h,b

def fetch(path, method="GET", data=None, hdrs=None, ctype=None, tries=40, sleepbase=0.5):
    delay=sleepbase
    for i in range(tries):
        code,h,b = once(path, method, data, hdrs, ctype=ctype)
        if code not in ("403","429","473","000"):
            return code,h,b,i+1
        time.sleep(delay+random.random()*0.7); delay=min(delay*1.25,5)
    return code,h,b,tries

if __name__=="__main__":
    paths = sys.argv[1:]
    for p in paths:
        t0=time.time()
        c,h,b,n = fetch(p)
        el=time.time()-t0
        print(f"{c} len={len(b)} tries={n} {el:.1f}s {p}")
