#!/usr/bin/env python3
import urllib.parse, requests, urllib3
urllib3.disable_warnings()
S = requests.Session(); S.verify=False
S.headers['User-Agent']='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
host='images'+'.'+'ctfassets.net'
img='https://%s/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg'%host
for w in (16,640,1080,3840):
    u='https://www.infinitycapital.bh/_next/image?url='+urllib.parse.quote(img,safe='')+'&w=%d&q=75'%w
    try:
        r=S.get(u,timeout=40,allow_redirects=False)
        print(w, r.status_code, len(r.content), r.headers.get('content-type'), r.headers.get('x-nextjs-cache'), r.headers.get('cache-control'))
    except Exception as e: print(w,'ERR',e)
