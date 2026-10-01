import subprocess, os

OUT="tool_outputs"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
log=[]
def t(desc,args):
    r=subprocess.run(["curl","-sk","-m","15"]+args+["-w","\\nHTTP:%{http_code} SIZE:%{size_download} XVM:%header{x-vercel-mitigated}\\n"],
                     capture_output=True,text=True)
    body=r.stdout.replace("\n"," ")[:200]
    log.append("### %s\nARGS: %s\nOUT: %s\nERR: %s\n"%(desc," ".join(args),r.stdout[:600],r.stderr[:200]))
    print("### %-40s => %s"%(desc,body),flush=True)

B="https://www.infinitycapital.bh/"
# 1. HTTP/1.0
t("http1.0",["--http1.0","-A",UA,B])
# 2. HEAD
t("HEAD",["-I","-A",UA,B])
# 3. XFF spoof
t("xff-spoof",["-A",UA,"-H","X-Forwarded-For: 8.8.8.8","-H","X-Real-IP: 8.8.8.8",B])
t("xff-cloudflare",["-A",UA,"-H","X-Forwarded-For: 1.1.1.1","-H","CF-Connecting-IP: 1.1.1.1",B])
# 4. curl-impersonate
if subprocess.run(["which","curl-impersonate"],capture_output=True).returncode==0:
    t("curl-impersonate-chrome",[""])
# 5. browser-ish sec headers
t("full-browser-headers",["-A",UA,"-H","Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
  "-H","Accept-Language: en-US,en;q=0.9","-H","Accept-Encoding: gzip, deflate, br",
  "-H","sec-ch-ua: \"Chromium\";v=\"124\", \"Google Chrome\";v=\"124\", \"Not-A.Brand\";v=\"99\"",
  "-H","sec-ch-ua-mobile: ?0","-H","sec-ch-ua-platform: \"Windows\"",
  "-H","Sec-Fetch-Dest: document","-H","Sec-Fetch-Mode: navigate","-H","Sec-Fetch-Site: none","-H","Sec-Fetch-User: ?1",
  "-H","Upgrade-Insecure-Requests: 1",B])
# 6. HTTP (no TLS) apex
t("http-plain",["-A",UA,"http://www.infinitycapital.bh/"])
# 7. apex host w/ Host header trick
t("host-header-apex",["-A",UA,"-H","Host: infinitycapital.bh","https://www.infinitycapital.bh/"])
open(OUT+"/waf_bypass.log","w").write("\n".join(log))
print("done")
