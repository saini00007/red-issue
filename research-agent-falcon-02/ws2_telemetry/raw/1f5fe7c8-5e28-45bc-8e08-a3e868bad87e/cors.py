import subprocess, json, os, uuid, time

B = "https://www.infinitycapital.bh"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

def run(args, name):
    f = "/tmp/c_" + uuid.uuid4().hex[:8]
    p = subprocess.run(["curl","-sk","--max-time","30","-D",f,"-o","/dev/null","-w","%{http_code}",
                        "-A",UA] + args, capture_output=True, text=True)
    h = open(f).read() if os.path.exists(f) else ""
    if os.path.exists(f): os.unlink(f)
    interesting = [l for l in h.splitlines()
                   if l.lower().startswith(("http/","access-control","vary","set-cookie","location","x-")) ]
    print(f"--- {name} -> {p.stdout}")
    for l in interesting: print("     ", l)
    print()

run(["-H","Origin: https://evil.example","-X","POST",B+"/api/send",
     "--form-string","fname=a","--form-string","lname=b","--form-string","msg=c",
     "--form-string","targets=info@infinitycapital.bh"], "POST /api/send Origin:evil")

run(["-X","OPTIONS","-H","Origin: https://evil.example",
     "-H","Access-Control-Request-Method: POST","-H","Access-Control-Request-Headers: content-type",
     B+"/api/send"], "OPTIONS preflight")

run(["-H","Origin: https://evil.example", B+"/api/send"], "GET /api/send Origin:evil")

run(["-H","Host: evil.example", B+"/"], "Host header injection")
run(["-H","X-Forwarded-Host: evil.example", "-H","X-Forwarded-Proto: http", B+"/"], "XFH override")
run(["-H","X-Original-URL: /admin", B+"/"], "X-Original-URL")
run([B+"/?next=https://evil.example/"], "open redirect probe")
run(["-H","Referer: https://evil.example/", B+"/contact"], "referer probe")
