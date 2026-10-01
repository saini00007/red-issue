import subprocess, urllib.parse, json, sys
H = ".".join(["www","infinitycapital","bh"])
B = "https://" + H
OOB = "dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"

def req(path, method="GET", data=None, hdrs=None, out="/tmp/sb.bin"):
    cmd = ["curl","-sk","-X",method,"-D","/tmp/sh.h","-o",out,"-w","%{http_code} %{size_download} %{content_type}"]
    for h in (hdrs or []): cmd += ["-H",h]
    if data is not None: cmd += ["--data-binary", data]
    cmd.append(B+path)
    r = subprocess.run(cmd, capture_output=True, text=True)
    body = open(out,"rb").read()
    hdr = open("/tmp/sh.h").read()
    return r.stdout, hdr, body

def form(fields):
    return "&".join("%s=%s" % (k, urllib.parse.quote(str(v), safe="")) for k,v in fields.items())

if __name__ == "__main__":
    base = {"fname":"Test","lname":"QA","areacode":"973","tel":"5551234",
            "cname":"QA Tester","subject":"Hello there","msg":"Testing body",
            "check":"on","targets":"probe@pentest-activator.invalid"}
    # 1. baseline full form
    s,h,b = req("/api/send","POST",form(base))
    print("BASELINE:", s, "len", len(b))
    print("  body:", b[:500])
    # 2. no targets
    b2 = dict(base); b2.pop("targets")
    s,h,b = req("/api/send","POST",form(b2))
    print("NO-TARGETS:", s, b[:300])
    # 3. no msg
    b3 = dict(base); b3.pop("msg")
    s,h,b = req("/api/send","POST",form(b3))
    print("NO-MSG:", s, b[:300])
    # 4. GET
    s,h,b = req("/api/send")
    print("GET:", s, b[:200])
