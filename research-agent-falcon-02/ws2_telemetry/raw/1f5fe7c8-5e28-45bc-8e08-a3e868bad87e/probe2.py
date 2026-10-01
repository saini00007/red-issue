import time, json
from send_lib import send, base

# The server says invalid 'to'. Maybe 'to' must be a valid email and is read from a field literally named to.
# But my 'to mass-assign' with a valid email still failed. So 'to' is server-derived from something else (targets -> lookup).
# Test: does the ORDER of fields matter? Does JSON body work? Let's try JSON.
import net2 as net
import json as J

# 1) JSON body with all fields incl 'to'
tests_json = [
    ("json to valid", dict(to="scanner@nothing.local", fname="V", lname="T", subject="s", msg="m", targets="1")),
    ("json no to", dict(fname="V", lname="T", subject="s", msg="m", targets="1")),
]
for name, d in tests_json:
    c, h, b = net.fetch("/api/send", method="POST", data=J.dumps(d),
                        ctype="application/json", tries=20, raw=True)
    print("### JSON", name, "->", c, len(b), b[:250])
    time.sleep(1.0)

# 2) multipart: what field names populate 'to'? Try email, recipient, mail, target
for fld in ["email", "recipient", "mail", "target", "targets", "sendto", "to[]"]:
    f = base()
    f[fld] = "scanner@nothing.local"
    c, h, b = send(f, tries=20)
    print("### field", fld, "->", c, b[:220])
    time.sleep(1.0)
