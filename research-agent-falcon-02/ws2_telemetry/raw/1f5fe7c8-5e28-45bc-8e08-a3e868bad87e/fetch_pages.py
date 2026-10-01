#!/usr/bin/env python3
import sys, os, re
sys.path.insert(0,'/work')
import icp
os.makedirs('/work/pages', exist_ok=True)
ROUTES = ['/', '/about', '/contact', '/investment-philosophy', '/investment-portfolio', '/privacy-terms', '/404']
for r in ROUTES:
    name = r.strip('/').replace('/','_') or 'root'
    c,b,h = icp.fetch(r, out='/work/pages/%s.html' % name)
    print(r, c, len(b))
    # save headers
    open('/work/pages/%s.hdr' % name,'w').write(h)
