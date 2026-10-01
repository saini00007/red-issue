import subprocess, sys, json

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
AT = chr(64)

def send(fields):
    args = ["curl","-sk","-A",UA,"-X","POST","https://www.infinitycapital.bh/api/send",
            "-H","Content-Type: application/x-www-form-urlencoded"]
    parts = []
    for k,v in fields.items():
        parts.append("--data-urlencode")
        parts.append(k+"="+v)
    args += parts + ["-o","/tmp/o.bin","-w","%{http_code}|%{size_download}"]
    r = subprocess.run(args, capture_output=True, text=True)
    body = open("/tmp/o.bin","rb").read()[:600]
    return r.stdout, body

base = {"fname":"probe","lname":"sec","areacode":"973","tel":"5551234",
        "cname":"qa","subject":"hello","msg":"body","check":"on"}

for cand in [ "sec" + AT + "infinitycapital.bh",
              "probe" + AT + "mailinator.com",
              "probe" + AT + "example" + AT + "x.com",
              "Probe <probe" + AT + "mailinator.com>" ]:
    f = dict(base); f["targets"] = cand
    code, body = send(f)
    print(cand, "->", code)
    print("   ", body)
