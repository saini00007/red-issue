import json, urllib.request, urllib.parse, sys, ssl
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
BASE="https://www.infinitycapital.bh/api/send"
def post(fields):
    d=urllib.parse.urlencode(fields).encode()
    r=urllib.request.Request(BASE,data=d,headers={'Content-Type':'application/x-www-form-urlencoded','User-Agent':'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(r,context=ctx,timeout=25) as resp:
            return resp.status, resp.read().decode('utf-8','replace')
    except Exception as e:
        return 'ERR', str(e)

def base(**kw):
    f={'fname':'aa','lname':'bb','areacode':'973','tel':'1234',
       'cname':'pentest'+('@infinity'+'capital' if False else '')+'','subject':'hello',
       'msg':'markerZZ91','check':'true','targets':'general'}
    f['cname']=kw.pop('cname', 'security'+'.report' + '@' + 'mailinator.com')
    f.update(kw)
    return f

if __name__=='__main__':
    for c in ['security.report@mailinator.com','pentest@infinitycapital.bh','a.b+tag@gmail.com']:
        s,b=post(base(cname=c))
        print('cname=',c,'->',s,b[:250])
    print('--- targets variants ---')
    for t in ['general','General','general,investment','{"general":true}',"['general']",'["general"]','']:
        s,b=post(base(targets=t))
        print('targets=',repr(t),'->',s,b[:250])
