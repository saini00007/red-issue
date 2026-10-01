import os, json
from ic9 import *
H = os.environ.get("RX","example.com")
A = "icp"+"robe"+"zz9"+"@"+H
tests = {
 "plain":              A,
 "display":            "Probe <"+A+">",
 "plus":               A.replace("@","+p@"),
 "subdomainish":       "icprobezz9@sub."+H,
 "nodot":              "icprobezz9@"+H.replace(".com",""),
 "comma-list":         A+", secondzz9@"+H,
 "semicolon":          A+"; secondzz9@"+H,
 "space-name":         "Probe "+A,
 "angle-inj":          "<"+A+">",
 "quoted":             '"'+A+'"',
 "crlf":               A+"\r\nBcc: secondzz9@"+H,
 "unicode-dot":        "icprobezz9@x"+".example.com",
 "targets-only":       None,
 "cname-empty":        "",
}
for k,v in tests.items():
    if k=="targets-only":
        jprint(send(cname="", targets=A), k)
    else:
        jprint(send(cname=v), k+" :: "+repr(v)[:60])
