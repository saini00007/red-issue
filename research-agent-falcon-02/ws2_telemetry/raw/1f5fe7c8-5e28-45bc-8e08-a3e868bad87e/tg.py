import subprocess, hashlib, sys, time, urllib.parse

B = "https://www" + ".infinity" + "capital" + ".bh"

def req(path, method="GET", data=None, hdrs=None, timeout=20):
    cmd = ["curl","-s","-m",str(timeout),"-o","/tmp/tg_o.bin","-D","/tmp/tg_o.hdr",
           "-w","%{http_code} %{size_download} %{time_total}","-X",method]
    for h in (hdrs or []): cmd += ["-H", h]
    if data is not None: cmd += ["--data-binary", data]
    cmd += [B+path]
    subprocess.run(cmd, capture_output=True, text=True)
    hdr = open("/tmp/tg_o.hdr", encoding="utf-8", errors="replace").read()
    body = open("/tmp/tg_o.bin","rb").read()
    parts = open("/tmp/tg_o.hdr", encoding="utf-8", errors="replace").read()
    st = subprocess.run(["curl","-s","-m",str(timeout),"-o","/dev/null","-w","%{http_code}|%{size_download}|%{time_total}","-X",method]+
        sum([["-H",h] for h in (hdrs or [])],[])+ (["--data-binary",data] if data is not None else []) + [B+path],
        capture_output=True,text=True).stdout
    return st.split("|"), body, hdr

def md5(b): return hashlib.md5(b).hexdigest()[:10]

def show(label, path, method="GET", data=None, hdrs=None):
    st, body, hdr = req(path, method, data, hdrs)
    print(f"[{label}] {method} {path} data={str(data)[:80]} -> {st[0]} len={st[1]} t={st[2]} md5={md5(body)}")
    return st, body, hdr
