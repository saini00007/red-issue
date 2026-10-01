import subprocess
B="https://www.infinitycapital.bh"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
targets = [
 ("root", B+"/"),
 ("about", B+"/about"),
 ("api", B+"/api/"),
 ("404", B+"/404"),
 ("next_image", B+"/_next/image?w=1080&q=75"),
 ("atom", B+"/atom.xml"),
 ("login", B+"/login"),
 ("robots", B+"/robots.txt"),
 ("securitytxt", B+"/.well-known/security.txt"),
]
for name,u in targets:
    r=subprocess.run(["curl","-sk","-m","15","-A",UA,"-H","Accept-Encoding: gzip, deflate",
                      "-D","/tmp/hh.txt","-o","tool_outputs/resp_%s.html"%name,
                      "-w","%{http_code} %{size_download}",u],capture_output=True,text=True)
    hdrs=open("/tmp/hh.txt").read()
    vm=[l.strip() for l in hdrs.splitlines() if "vercel-mitigated" in l.lower()]
    print("%-11s %-10s mitigated=%s" % (name, r.stdout, vm[0] if vm else "none"), flush=True)
