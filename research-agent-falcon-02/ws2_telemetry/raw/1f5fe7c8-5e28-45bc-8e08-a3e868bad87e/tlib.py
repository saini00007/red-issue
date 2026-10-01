import subprocess,os,time,sys

W=os.environ['WORK_PATH']
D='/work/tool_outputs'
os.makedirs(D,exist_ok=True)

def curl(args, timeout=30):
    cmd=['bash',W+'/rq.sh']+args
    return subprocess.run(cmd,capture_output=True,text=True,timeout=timeout)

def get(path, tries=8):
    """GET with retry on 403 checkpoint / 429"""
    for i in range(tries):
        r=curl(['-o','/dev/null','-w','%{http_code}',path and 'https://www.infinitycapital.bh'+path or 'https://www.infinitycapital.bh/'])
        c=r.stdout.strip()
        if c in ('200','404','308','301','302','500','400','405'):
            return int(c)
        time.sleep(4+3*i)
    return int(c) if c.isdigit() else 0

def post(path, fields, tries=8, extra_hdrs=None):
    """fields: dict or list of (k,v) or raw string"""
    body = fields if isinstance(fields,str) else '&'.join(
        f"{k}={str(v).replace(' ','%20').replace(chr(39),'%27')}" for k,v in fields)
    for i in range(tries):
        cmd=['-X','POST','-w','%{http_code}','-D','/tmp/ph.txt']
        if extra_hdrs:
            for h in extra_hdrs: cmd+=['-H',h]
        cmd+=['-F',body,'https://www.infinitycapital.bh'+path]
        r=curl(cmd)
        c=r.stdout.strip()[-3:]
        if c in ('200','404','500','400','405','422'):
            return int(c), r.stdout
        time.sleep(4+3*i)
    return 0, r.stdout

def save(name, txt):
    p=os.path.join(D,name)
    open(p,'w').write(txt)
    return p
