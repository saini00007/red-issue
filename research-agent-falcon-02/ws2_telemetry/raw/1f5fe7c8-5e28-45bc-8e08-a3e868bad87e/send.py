import sys, json, uuid
sys.path.insert(0,".")
from net import fetch, UA_GBOT

def send(fields, files=None, tag="t"):
    boundary="----ICVAPT%s"%uuid.uuid4().hex
    body=b""
    for k,v in fields.items():
        body+=("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n"%(boundary,k,v)).encode()
    for k,(fn,ct,content) in (files or {}).items():
        body+=("--%s\r\nContent-Disposition: form-data; name=\"%s\"; filename=\"%s\"\r\nContent-Type: %s\r\n\r\n"%(boundary,k,fn,ct)).encode()
        body+=content.encode() if isinstance(content,str) else content
        body+=b"\r\n"
    body+=("--%s--\r\n"%boundary).encode()
    return fetch("/api/send", method="POST", data=body, ctype="multipart/form-data; boundary="+boundary, ua=UA_GBOT, tries=25)

base=dict(fname="Test", lname="User", areacode="+973", tel="3600000", cname="VAPT Tester",
           subject="Investment enquiry", msg="Hello from authorized VAPT test, ref "+uuid.uuid4().hex[:8],
           check="", targets="1")
c,h,b = send(base)
print("VALID:",c,len(b),b[:500])
print([l for l in h.splitlines() if "matched" in l.lower() or "cache" in l.lower()])
