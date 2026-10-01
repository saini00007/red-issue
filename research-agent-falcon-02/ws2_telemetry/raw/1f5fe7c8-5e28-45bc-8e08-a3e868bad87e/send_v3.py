import subprocess, time, json
B = "https://www.infinitycapital.bh/api/send"
MAIL = "probe@www.infinitycapital.bh"

def post(fields):
    cmd = ["curl","-s","-o","/tmp/r.bin","-D","/tmp/r.hdr","-m","40","-X","POST",B]
    for k,v in fields.items(): cmd += ["-F", f"{k}={v}"]
    subprocess.run(cmd, capture_output=True, text=True)
    hdr = open("/tmp/r.hdr", errors="ignore").read()
    body = open("/tmp/r.bin","rb").read()
    return (hdr.splitlines()[0] if hdr else "NONE"), len(body), body[:500]

def base(**kw):
    d = {"fname":"Test","lname":"User","areacode":"973","tel":"1234567",
         "cname":"Test User","subject":"Inquiry","msg":"hello there","check":"","targets":"[]"}
    d.update(kw); return d

tests = [
 ("arr_email_str",  {"targets": json.dumps([MAIL])}),
 ("arr_email_obj",  {"targets": json.dumps([{"email": MAIL, "name":"P"}])}),
 ("arr_obj_val",    {"targets": json.dumps([{"value": MAIL, "label":"P"}])}),
 ("plain_email",    {"targets": MAIL}),
 ("csv",            {"targets": "a@b.com,"+MAIL}),
 ("named",          {"targets": json.dumps(["Probe <"+MAIL+">"])}),
 ("plus_addr",      {"targets": json.dumps(["probe+ic@"+"www.infinitycapital.bh"])}),
 ("two_emails",     {"targets": json.dumps([MAIL, "probe2@www.infinitycapital.bh"])}),
]
for k, kw in tests:
    try: r = post(base(**kw))
    except Exception as e: r = ("EXC",0,str(e).encode())
    print(f"{k:16s} {r[0]:14s} {r[1]:5d} {r[2][:300]!r}", flush=True)
    time.sleep(1.5)
