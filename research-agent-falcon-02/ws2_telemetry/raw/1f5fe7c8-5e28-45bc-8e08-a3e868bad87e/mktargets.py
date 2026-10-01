#!/usr/bin/env python3
import urllib.parse, os
host='images'+'.'+'ctfassets.net'
img='https://%s/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg'%host
q=urllib.parse.quote(img,safe='')
B='https://www.infinitycapital.bh'
O='/work/tool_outputs'
tgts = {
 'img'   : f'{B}/_next/image?url={q}&w=1080&q=75',
 'imgw'  : f'{B}/_next/image?w=1080',
 'imgq'  : f'{B}/_next/image?url={q}&q=75',
 'contact': f'{B}/contact?x=1&cb=1&q=test',
 'contactx': f'{B}/contact?x=1',
 'home'  : f'{B}/?id=1&search=test&page=2',
 'apiid' : f'{B}/api/?id=1&page=2',
 'e404'  : f'{B}/404?q=test',
}
p=os.path.join(O,'sqli_targets.txt')
with open(p,'w') as f:
    for k,v in tgts.items(): f.write(f'{k}\t{v}\n')
print(open(p).read())
