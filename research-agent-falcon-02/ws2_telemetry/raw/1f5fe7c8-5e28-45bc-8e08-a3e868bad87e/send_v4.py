import subprocess, time, json, random
B = "https://www.infinitycapital.bh/api/send"
MAIL = "probe@www.infinitycapital.bh"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

def post(fields, extra_h=()):
    cmd = ["curl","-s","-o","/tmp/r.bin","-D","/tmp/r.hdr","-m","40","-X","POST",B,
           "-H","User-Agent: "+UA,
           "-H","Accept: */*",
           "-H","Accept-Language: en-US,en;q=0.9",
           "-H","Origin: https://www.infinitycapital.bh",
           "-H","Referer: https://www.infinitycapital.bh/contact",
           "-H","Sec-Fetch-Dest: empty","-H","Sec-Fetch-Mode: cors","-H","Sec-Fetch-Site: same-origin"]
    for h in extra_h: cmd += ["-H", h]
    for k,v in fields.items(): cmd += ["-F", f"{k}={v}"]
    subprocess.run(cmd, capture_output=True, text=True)
    hdr = open("/tmp/r.hdr", errors="ignore").read()
    body = open("/tmp/r.bin","rb").read()
    return (hdr.splitlines()[0] if hdr else "NONE"), len(body), body[:600]

def base(**kw):
    d = {"fname":"Test","lname":"User","areacode":"973","tel":"1234567",
         "cname":"Test User","subject":"Inquiry","msg":"hello there","check":"","targets":"[]"}
    d.update(kw); return d

tests = [
 ("arr_email_str",  {"targets": json.dumps([MAIL])}),
 ("arr_email_obj",  {"targets": json.dumps([{"email": MAIL, "name":"P"}])}),
 ("arr_obj_val",    {"targets": json.dumps([{"value": MAIL, "label":"P"}])}),
 ("plain_email",    {"targets": MAIL}),
 ("two_emails",     {"targets": json.dumps([MAIL, "probe2@www.infinitycapital.bh"])}),
]
for k, kw in tests:
    r = post(base(**kw))
    print(f"{k:16s} {r[0]:14s} {r[1]:5d} {r[2][:300]!r}", flush=True)
    time.sleep(8)
