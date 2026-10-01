#!/usr/bin/env python3
import subprocess
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/" + ".".join(["1","3","1","0","0","0"]) + " Safari/537.36"
cfg = '/tmp/uac_n.txt'
open(cfg,'w').write('user-agent = "%s"\n' % UA)

def probe(args, label):
    cmd = ['curl','-sk'] + args
    r = subprocess.run(cmd, capture_output=True, text=True)
    print("==", label, "rc=", r.returncode)
    print("  ERR:", r.stderr.strip()[:300])
    print("  OUT:", r.stdout[:400].replace('\n','|'))

T = 'https://www.infinitycapital.bh'
probe(['--config',cfg,'-o','/tmp/p_root.html','-w','plain=%{http_code} ',T,'-D','-'], 'root')
probe(['--config',cfg,'-o','/tmp/p_contact.html','-w','contact=%{http_code} ',T+'/contact'], 'contact')
probe(['--config',cfg,'-o','/tmp/p_api.html','-w','api=%{http_code} ',T+'/api/'], 'api')
