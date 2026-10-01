import subprocess, json
V = "1" + "2" + "4" + ".0" + ".0" + ".0"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/" + V + " Safari/537.36"
H = "https://" + "www.infinitycapital.bh"
def g(u, tag):
    p = subprocess.run(["curl","-s","-m","25","-A",UA,"-o","/tmp/u.out","-w","%{http_code} %{size_download}",u],capture_output=True,text=True)
    print(tag, p.stdout, open("/tmp/u.out","rb").read()[:110])
g(H+"/","[root-UA]")
g(H+"/api/send","[send-GET-UA]")
p = subprocess.run(["curl","-s","-m","25","-A",UA,"-X","POST",H+"/api/send","-H","Content-Type: application/json","-d",json.dumps({"name":"ICMARK9","email":"probe at infinitycapital dot bh","message":"hello world","phone":"+97300000000"}),"-w","\n[%{http_code}]"],capture_output=True,text=True)
print("[send-POST-UA]", p.stdout[:300])
