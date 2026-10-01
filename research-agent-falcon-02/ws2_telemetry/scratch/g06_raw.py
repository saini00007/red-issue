import os, re, collections
ROOT="/var/lib/scanner"
HOST=[os.path.join(ROOT,h) for h in sorted(os.listdir(ROOT)) if os.path.isdir(os.path.join(ROOT,h))][0]
files=[]
for sid in sorted(os.listdir(HOST)):
    d=os.path.join(HOST,sid); p=os.path.join(d,"logs","agent.log")
    if os.path.isfile(p): files.append((sid,p))
# find raw lines mentioning ledger.resolve and show RAW shape (redacted endpoint)
n=0
for sid,p in files:
    for ln in open(p,encoding="utf-8",errors="replace"):
        if "ledger.resolve" in ln:
            n+=1
            if n<=3:
                red=re.sub(r'endpoint=\S+','endpoint=<REDACTED>',ln.rstrip())
                red=re.sub(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}','<uuid>',red)
                print(sid[:8],"::",red[:260])
print("TOTAL lines containing 'ledger.resolve':",n)