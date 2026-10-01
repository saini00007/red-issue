import sys, re, json, urllib.parse
sys.path.insert(0,"w13")
from sess import req, B

CDN="https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg"
E=urllib.parse.quote(CDN, safe="")

def show(name, r, n=400):
    t=r.text or ""
    print("---",name,"status",r.status_code,"len",len(t),"ct",r.headers.get("content-type"))
    body=re.sub(r"<script.*?</script>","",t,flags=re.S)
    print("   snippet:", repr(body[:n]))

# 1) valid image request
r=req("/_next/image", params={"url":E,"w":"1080","q":"75"})
show("valid", r, 200)
print("   ct-detail", r.headers.get("content-type"), "len", len(r.content))

# 2) missing url -> what error
r2=req("/_next/image")
show("nourl", r2, 600)

# 3) bad w
r3=req("/_next/image", params={"url":E,"w":"abc","q":"75"})
show("badw", r3, 600)

# 4) does 400 body reflect the url param? marker
MARK="ZZMARK9XZQ"
r4=req("/_next/image", params={"url":MARK,"w":"1080","q":"75"})
t=r4.text
print("MARK reflected in 400 body:", MARK in t, "| status", r4.status_code, "len", len(t))
if MARK in t:
    i=t.find(MARK); print("   ctx:", repr(t[max(0,i-200):i+200]))
