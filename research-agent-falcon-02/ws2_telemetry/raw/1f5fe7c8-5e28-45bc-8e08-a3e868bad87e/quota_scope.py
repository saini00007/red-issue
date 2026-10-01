import urllib.request,urllib.parse,ssl
ctx=ssl.create_default_context();ctx.check_hostname=False;ctx.verify_mode=ssl.CERT_NONE
H="www.infinitycapital.bh"
URL="https://"+H+"/api/send"
def post(f):
    r=urllib.request.Request(URL,data=urllib.parse.urlencode(f).encode(),
      headers={'Content-Type':'application/x-www-form-urlencoded','User-Agent':'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(r,context=ctx,timeout=20) as x: return x.status,x.read().decode()[:200]
    except Exception as e:
        try: return e.code,e.read().decode()[:200]
        except: return 'ERR',str(e)
b={'fname':'aa','lname':'bb','areacode':'973','tel':'1234','cname':'x@'+H,'subject':'s','msg':'m','check':'true'}
print("QUOTA SCOPE TEST")
for tgt in ['info@'+H,'sales@'+H,'x1@'+H,'admin@'+H]:
    f=dict(b); f['targets']=tgt
    print(' ',tgt, post(f))
f=dict(b); f['targets']='notanemail'
print(' invalid targets ->', post(f))
