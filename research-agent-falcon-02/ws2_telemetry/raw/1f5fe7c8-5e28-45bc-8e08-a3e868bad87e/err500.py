import urllib.request,urllib.parse,ssl
ctx=ssl.create_default_context();ctx.check_hostname=False;ctx.verify_mode=ssl.CERT_NONE
H="www.infinitycapital.bh"; URL="https://"+H+"/api/send"
def req(data=None, method='POST', hdrs=None):
    h={'User-Agent':'Mozilla/5.0'}
    if hdrs: h.update(hdrs)
    body=None
    if data is not None:
        if 'multipart' in h.get('Content-Type',''):
            body=data
        else:
            h.setdefault('Content-Type','application/x-www-form-urlencoded'); body=urllib.parse.urlencode(data).encode()
    r=urllib.request.Request(URL,data=body,headers=h,method=method)
    try:
        with urllib.request.urlopen(r,context=ctx,timeout=20) as x:
            return x.status, dict(x.headers), x.read().decode('utf-8','replace')[:400]
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode('utf-8','replace')[:800]
    except Exception as e:
        return 'ERR', {}, str(e)

print("GET /api/send ->", req(None,'GET')[0::2])
b={'fname':'aa','lname':'bb','areacode':'973','tel':'1234','cname':'x@'+H,'subject':'s','msg':'m','check':'true','targets':'notanemailX'}
print("POST invalid targets ->", req(b)[0::2])
# array/object injection shapes
import json
for shape in [
  {'fname':['a']}, {'fname':{'a':'b'}}, {'cname':['a','b']},
  {'targets':['a','b']}, {'msg':['x']}, {'check':{'x':1}},
  {'fname':None}, {'fname':''}, {'tel':None},
]:
    f=dict(b); f.update(shape)
    s,h,body=req(f)
    print(shape,'->',s,body[:220])
