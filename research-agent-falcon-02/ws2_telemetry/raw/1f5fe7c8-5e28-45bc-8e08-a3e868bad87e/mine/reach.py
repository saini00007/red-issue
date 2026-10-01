import urllib.parse, subprocess, sys
CTF = "https://" + "images.ctfassets.net" + "/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg"
img = urllib.parse.quote(CTF, safe='')
urls = [
 "https://www.infinitycapital.bh/",
 "https://www.infinitycapital.bh/api/",
 "https://www.infinitycapital.bh/api/?id=1",
 "https://www.infinitycapital.bh/api/send",
 "https://www.infinitycapital.bh/contact?cb=1",
 "https://www.infinitycapital.bh/?id=1&search=test&page=2",
 "https://www.infinitycapital.bh/_next/image?url="+img+"&w=1080&q=75",
 "https://www.infinitycapital.bh/_next/image?url=&w=1080&q=75",
 "https://www.infinitycapital.bh/atom.xml",
 "https://www.infinitycapital.bh/feeds/all.atom.xml",
 "https://www.infinitycapital.bh/404",
 "https://www.infinitycapital.bh/robots.txt",
]
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
for u in urls:
    out = subprocess.run(["curl","-s","-o","/dev/null","-w","%{http_code} %{size_download} %{content_type}","-A",UA,u],capture_output=True,text=True).stdout
    print(f"{u[:95]:<95} {out}")
