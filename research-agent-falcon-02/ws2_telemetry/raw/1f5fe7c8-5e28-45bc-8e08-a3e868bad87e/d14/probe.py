import urllib.request, urllib.parse, json, ssl
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
def req(url,data=None,method=None,extra=None):
    h={"User-Agent":UA,"Accept":"*/*"}
    if extra: h.update(extra)
    r=urllib.request.Request(url,data=data,headers=h,method=method)
    try:
        resp=urllib.request.urlopen(r,timeout=15,context=ctx)
        return resp.status,dict(resp.headers),resp.read()
    except urllib.error.HTTPError as e:
        return e.code,dict(e.headers),e.read()
    except Exception as e:
        return -1,{},str(e).encode()
def show(tag,*a):
    s,h,b=a
    print("[%s] %s len=%d ct=%s srv=%s" % (tag,s,len(b),h.get('Content-Type'),h.get('Server')))
    print("   body:",b[:250])
B="https://www.infinitycapital.bh"
img="https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg"
show("nextimage-ctf",*req(B+"/_next/image?url="+urllib.parse.quote(img,safe="")+"&w=1080&q=75"))
rcpt="probe@localhost.invalid"
show("send-GET",*req(B+"/api/send"))
show("send-POST-json",*req(B+"/api/send",data=json.dumps({"targets":rcpt,"subject":"t","message":"m"}).encode(),method="POST",extra={"Content-Type":"application/json"}))
show("send-POST-form",*req(B+"/api/send",data=urllib.parse.urlencode({"targets":rcpt,"subject":"t","message":"m"}).encode(),method="POST",extra={"Content-Type":"application/x-www-form-urlencoded"}))
show("send-OPTIONS",*req(B+"/api/send",method="OPTIONS"))
show("home",*req(B+"/"))
show("contact",*req(B+"/contact"))