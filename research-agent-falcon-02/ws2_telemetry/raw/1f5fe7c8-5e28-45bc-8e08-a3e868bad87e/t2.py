import sys, uuid
sys.path.insert(0,".")
from send import send

def T(name, targets=None, extra=None, files=None):
    f=dict(fname="Test", lname="User", areacode="+973", tel="3600000", cname="VAPT",
           subject="Enquiry", msg="probe "+uuid.uuid4().hex[:6], check="", targets=targets or "")
    if extra: f.update(extra)
    c,h,b=send(f, files=files)
    print(f"[{name}] {c} {b[:300]}")
    return c,b

many=", ".join("r%d@evil.example"%i for i in range(1,11))
T("10-recipients", many)
T("crlf-in-name", "IC\r\nBcc: spy@evil.example\r\nX-Injected: yes@evil.example")
T("cc-attempt", 'attacker@evil.example" , "CC: spy@evil.example')
T("url-in-msg", None, {"msg":"<a href='http://x'>x</a>"})
