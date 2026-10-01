import sys, time, hashlib
sys.path.insert(0,'/work/tool_outputs')
from w40_lib import req, form

BASE = {'fname':'probe','lname':'Security','areacode':'973','tel':'5551234',
        'cname':'QA Tester','subject':'Hello there','msg':'Testing message body',
        'check':'on','targets':'probe@relay.invalid'}

cases = [
 ("quote_only", dict(BASE, fname="o'brien")),
 ("quote_msg", dict(BASE, msg="o'brien")),
 ("sqli_and", dict(BASE, msg="x' AND '1'='1")),
 ("plain", dict(BASE)),
 ("sleep", dict(BASE, msg="x' AND SLEEP(5)-- -")),
]
for name,d in cases:
    t=time.time(); st,h,b = req("/api/send", form(d)); el=time.time()-t
    print("%-12s code=%s len=%d t=%.2f  %r" % (name, st, len(b), el, b[:120]))
    time.sleep(6)
