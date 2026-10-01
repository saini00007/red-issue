import urllib.request, urllib.parse
BASE="https://www.infinitycapital.bh/api/send"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
def post(fields, ctype="application/x-www-form-urlencoded"):
    raw=urllib.parse.urlencode(fields).encode() if ctype.endswith("urlencoded") else fields.encode()
    req=urllib.request.Request(BASE,data=raw,headers={"User-Agent":UA,"Content-Type":ctype,"Accept":"*/*"})
    try:
        r=urllib.request.urlopen(req,timeout=40); return r.status, dict(r.headers), r.read()[:400]
    except Exception as e:
        h=dict(e.headers) if hasattr(e,'headers') else {}
        try: b=e.read()[:400]
        except: b=b""
        return getattr(e,'code',0), h, b

print(post({"fname":"T","lname":"U","areacode":"973","tel":"5551234","cname":"C","subject":"S","msg":"M","check":"on","to":"info@infinitycapital.bh"}))
print(post({"fname":"T","lname":"U","areacode":"973","tel":"5551234","cname":"C","subject":"S","msg":"M","check":"on","to":"probe@www.infinitycapital.bh","replyTo":"a@b.c"}))
print(post({"to":"info@infinitycapital.bh","message":"hi","subject":"s"}))
# what about verbose error / stack?
st,h,b=post({"to":"x@y.z"})
print("HDRS",h)
print("BODY",b)