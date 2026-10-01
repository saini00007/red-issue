import sys, time, json, re
sys.path.insert(0,'/work/tool_outputs')
from w40_lib import req, form

BASE = {'fname':'idorprobe','lname':'Security','areacode':'973','tel':'5551234',
        'cname':'QA Tester','subject':'Hello there','msg':'Testing message body',
        'check':'on','targets':'probe@relay.invalid'}

st,h,b = req("/api/send", form(BASE))
print("submit:", st, b[:200])
m = re.search(rb'"id":"([^"]+)"', b)
mid = m.group(1).decode() if m else None
print("MY_ID:", mid)
time.sleep(6)

# probe retrieval of the submission object (IDOR / read-back)
paths = [
  "/api/send/" + (mid or "x"),
  "/api/send?id=" + (mid or "x"),
  "/api/messages/" + (mid or "x"),
  "/api/message/" + (mid or "x"),
  "/api/submissions/" + (mid or "x"),
  "/api/contact/" + (mid or "x"),
  "/api/inbox",
  "/api/messages",
  "/api/send?action=list",
  "/api/admin",
  "/api/admin/messages",
  "/api/dashboard",
]
for p in paths:
    st,h,b = req(p)
    print("%-70s %s len=%d %r" % (p[:70], st, len(b), b[:110]))
    time.sleep(1.2)
