import subprocess, json
T="https://"+"www.infinity"+"capital"+"."+"bh"
CDN="https://"+"images."+"ctfassets"+"."+"net"
IMG=CDN+"/yts1dx0j7jj5/yRvqRHKqEsbLvrma0OXqV/4b64635f8f18ab2e546275054c0f0230/infinity.jpg"
import urllib.parse
E=urllib.parse.quote(IMG,safe="")
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

def req(path, method="GET", data=None, ct=None):
    cmd=["curl","-s","-m","25","-D","/tmp/p1.hdr","-o","/tmp/p1.bin","-w","%{http_code} %{size_download}","-A",UA]
    if ct: cmd+=["-H","Content-Type: "+ct]
    if data: cmd+=["--data-binary",data]
    cmd+=[T+path, "-X", method]
    r=subprocess.run(cmd,capture_output=True,text=True)
    h=open("/tmp/p1.hdr").read() if __import__('os').path.exists("/tmp/p1.hdr") else ""
    b=open("/tmp/p1.bin","rb").read() if __import__('os').path.exists("/tmp/p1.bin") else b""
    return r.stdout.strip(), h, b

tests=[("/_next/image?url="+E+"&w=1080&q=75","GET",None,None),
       ("/api/send","POST",'{}',"application/json"),
       ("/api/contact","POST",'{}',"application/json"),
       ("/contact","GET",None,None),
       ("/api/send","GET",None,None)]
for p,m,d,c in tests:
    st,h,b=req(p,m,d,c)
    print("PATH",p,"->",st,"|mitigated=", [l for l in h.splitlines() if 'erculated' in l or 'erced' in l])
    if b and len(b)<2000: print("   BODY:",b[:600])
