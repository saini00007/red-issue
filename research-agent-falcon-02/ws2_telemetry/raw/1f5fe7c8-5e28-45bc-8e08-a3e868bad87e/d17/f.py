import requests, os, sys, json
U = open('/work/ua_final.txt').read().strip()
H = {'User-Agent': U, 'Accept':'*/*'}
T = "https://www.infinitycapital.bh"
OUT = os.path.join(os.environ.get('WORK_PATH', '.'), 'tool_outputs')
os.makedirs(OUT, exist_ok=True)

def get(name, path, **kw):
    r = requests.get(T+path, headers=H, timeout=30, allow_redirects=True, **kw)
    fn = os.path.join(OUT, 'd17_%s' % name)
    open(fn+'.bin','wb').write(r.content)
    open(fn+'.hdr','w').write(str(r.status_code)+'\n'+str(r.headers))
    print(name, r.status_code, len(r.content), r.headers.get('content-type'))
    if 'text' in (r.headers.get('content-type') or '') or 'json' in (r.headers.get('content-type') or ''):
        print('   body:', r.text[:300].replace('\n',' '))
    return r

if __name__ == '__main__':
    for n,p in json.load(open(sys.argv[1])):
        get(n,p)
