import subprocess
DOM = "dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
hosts = [
 "oob571a47f26f8c",  # control probe (expect callback -> oracle live)
 "oob17aecfd7c311", "oobce880a03ecdf", "oob2d43988f0966",
 "oob0ef589439eb2", "oob6808dd4b32ce", "ooba76cef8510c5", "oob12972aecd78e",
]
for tok in hosts:
    url = "http://" + tok + "." + DOM + "/"
    r = subprocess.run(["curl","-s","-m","8","-o","/dev/null","-w","%{http_code}",url],capture_output=True,text=True)
    print("%-16s http=%s" % (tok, r.stdout), flush=True)
