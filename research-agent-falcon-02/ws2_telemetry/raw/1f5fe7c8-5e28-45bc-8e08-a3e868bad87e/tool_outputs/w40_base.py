import sys, hashlib, time
sys.path.insert(0,'/work/tool_outputs')
from w40_lib import req, form

BASE = {'fname':'sqlmapProbe','lname':'Security','areacode':'973','tel':'5551234',
        'cname':'QA Tester','subject':'Hello there','msg':'Testing message body',
        'check':'on','targets':'sqli-probe@relay.invalid'}

cases = [("baseline", dict(BASE)),
         ("sqli_fname", dict(BASE, fname="sqlmapProbe' OR '1'='1")),
         ("sqli_msg", dict(BASE, msg="body' AND SLEEP(0)-- -")),
         ("meta_fname", dict(BASE, fname="foo{{7*7}}bar")),
         ("cmdi_fname", dict(BASE, fname="foo;id")),
         ("no_check", {k:v for k,v in BASE.items() if k!='check'}),
         ("empty_body", None),
        ]
for name, d in cases:
    t=time.time()
    st,h,b = req("/api/send", form(d) if d is not None else "")
    el=time.time()-t
    print("%-14s code=%s len=%d h=%s t=%.2f" % (name, st, len(b), hashlib.md5(b).hexdigest()[:10], el))
    print("    vercel-mitigated=%s ct=%s body=%r" % (h.get('x-vercel-mitigated'), h.get('content-type'), b[:160]))
