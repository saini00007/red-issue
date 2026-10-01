#!/usr/bin/env python3
import sys, os, re, glob
sys.path.insert(0,'/work')
import icp
srcs = set()
for f in glob.glob('/work/pages/*.html'):
    s = open(f, encoding='utf-8', errors='replace').read()
    srcs |= set(re.findall(r'src="([^"]*\.js[^"]*)"', s))
os.makedirs('/work/jsx', exist_ok=True)
for s in sorted(srcs):
    name = s.split('/')[-1].replace('%5B','').replace('%5D','')
    c,b,h = icp.fetch(s, out='/work/jsx/'+name)
    print(c, len(b), name)
