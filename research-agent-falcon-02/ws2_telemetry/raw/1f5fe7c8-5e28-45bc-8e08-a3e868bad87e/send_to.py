import json, urllib.request, urllib.parse, ssl
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
BASE="https://www.infinitycapital.bh/api/send"
def post(fields, files=None):
    if files:
        boundary='----ICX'
        body=b''
        for k,v in fields.items():
            body+=('--%s\r\nContent-Disposition: form-data; name="%s"\r\n\r\n%s\r\n'%(boundary,k,v)).encode()
        for k,(fn,content,ct) in files.items():
            body+=('--%s\r\nContent-Disposition: form-data; name="%s"; filename="%s"\r\nContent-Type: %s\r\n\r\n'%(boundary,k,fn,ct)).encode()+content+b'\r\n'
        body+=('--%s--\r\n'%boundary).encode()
        r=urllib.request.Request(BASE,data=body,headers={'Content-Type':'multipart/form-data; boundary=%s'%boundary,'User-Agent':'Mozilla/5.0'})
    else:
        r=urllib.request.Request(BASE,data=urllib.parse.urlencode(fields).encode(),
          headers={'Content-Type':'application/x-www-form-urlencoded','User-Agent':'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(r,context=ctx,timeout=25) as resp:
            return resp.status, resp.read().decode('utf-8','replace')
    except Exception as e:
        try: return e.code, e.read().decode('utf-8','replace')
        except Exception: return 'ERR', str(e)

def base(**kw):
    f={'fname':'aa','lname':'bb','areacode':'973','tel':'1234',
       'cname':'test.investigator@protonmail.com','subject':'hello','msg':'markerZZ91',
       'check':'true','targets':'info@infinitycapital.bh'}
    f.update(kw); return f

tests=[
 ('targets=info@infinitycapital.bh', base()),
 ('targets=Name <info@infinitycapital.bh>', base(targets='Name <info@infinitycapital.bh>')),
 ('targets=info@infinitycapital.bh,finance@infinitycapital.bh', base(targets='info@infinitycapital.bh,finance@infinitycapital.bh')),
 ('targets=[]', base(targets='[]')),
 ('targets=[a@b.c]', base(targets='["info@infinitycapital.bh"]')),
]
for name,f in tests:
    s,b=post(f); print(name,'->',s,b[:300]); print()
