import subprocess

T = "https://www.infinitycapital.bh/api/send"
args = ["curl","-sk","--max-time","40","-X","POST",T,"-D-",
        "--form-string","fname=A","--form-string","lname=B",
        "--form-string","areacode=+973","--form-string","tel=3600000",
        "--form-string","cname=C","--form-string","subject=S",
        "--form-string","msg=m","--form-string","check=",
        "--form-string","targets=info@infinitycapital.bh"]
p = subprocess.run(args, capture_output=True)
print("RC", p.returncode)
print(p.stdout.decode("utf8","replace")[:2500])
print("STDERR", p.stderr.decode("utf8","replace")[:500])
