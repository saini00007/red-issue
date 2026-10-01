import subprocess, re, time
H = "infinity" + "capital" + "." + "bh"
S = "https://www." + H + "/api/send"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0 Safari/537.36"


def send(targets, fname="QA"):
    d = dict(fname=fname, lname="Tester", areacode="973", tel="5551234",
             cname="QA Tester", subject="probe", msg="probe body", check="on")
    if targets is not None:
        d["targets"] = targets
    args = ["curl", "-s", "-i", "-X", "POST", S, "-A", UA]
    for k, v in d.items():
        args += ["-F", "%s=%s" % (k, v)]
    r = subprocess.run(args, capture_output=True, timeout=40, text=True).stdout
    parts = re.split(r"\r?\n\r?\n", r, 1)
    status = parts[0].split("\n")[0].strip()
    body = parts[-1][:220].replace("\n", " ")
    return status, body


ts = int(time.time())
cases = [
    ("OMIT targets", None),
    ("targets=garbage (not email)", "garbage-not-an-email"),
    ("targets=EXT attacker domain (protonmail)", "sectest%da@protonmail.com" % ts),
    ("targets=EXT attacker domain (gmail)", "sectest%db@gmail.com" % ts),
    ("targets=EXT attacker domain (yahoo)", "sectest%dc@yahoo.com" % ts),
    ("targets display-name fmt", "QA <sectest%dd@protonmail.com>" % ts),
    ("targets comma-list 2 ext", "x1@protonmail.com, x2@gmail.com"),
]
for name, t in cases:
    st, bd = send(t)
    print("[%s]\n   %s\n   %s\n" % (name, st, bd), flush=True)
