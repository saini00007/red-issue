import requests, sys
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"}
B="https://www.infinitycapital.bh"
paths=[
 "/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75",
 "/api/send","/contact","/api/","/404","/atom.xml","/feeds/all.atom.xml",
 "/?%24p=1","/?id=1&search=test&page=2","/contact?cb=1",
]
for p in paths:
    try:
        r=requests.get(B+p,headers=UA,timeout=25,allow_redirects=True)
        print(r.status_code, len(r.content), p, "->", r.url)
    except Exception as e:
        print("ERR",p,e)
