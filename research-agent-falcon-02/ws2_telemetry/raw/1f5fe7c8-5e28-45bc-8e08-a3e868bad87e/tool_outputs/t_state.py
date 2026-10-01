import sys, time, subprocess
sys.path.insert(0,".")
from ic import post, build, get, HOST, UA

def show(label, tries=12, **kw):
    raw = kw.pop("raw", None)
    code, hdr, bd, n = post(build(**kw), raw=raw, tries=tries)
    print("--- %s -> HTTP %s (try %d)" % (label, code, n))
    print("   ", bd[:300].replace("\n"," "))
    return code, bd

print("== does 429 precede validation? (invalid targets while quota-exhausted) ==")
show("invalid targets now", targets="not-an-email")
print("== missing targets now ==")
show("no targets now", raw="fname=T&lname=U&areacode=973&tel=1&cname=C&subject=S&msg=m&check=on")

print()
print("== is there any auth/session requirement at all? ==")
# no cookies, no auth header, foreign Origin -> already done. Test CORS preflight
r = subprocess.run(["curl","-s","-m","20","-i","-X","OPTIONS",HOST+"/api/send",
  "-H","Origin: https://evil.example","-H","Access-Control-Request-Method: POST",
  "-H","Access-Control-Request-Headers: content-type"], capture_output=True, text=True)
print(r.stdout[:900])
