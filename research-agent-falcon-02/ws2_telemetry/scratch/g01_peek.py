import os, json, collections, re
ROOT="/var/lib/scanner"
HOST=[os.path.join(ROOT,h) for h in sorted(os.listdir(ROOT)) if os.path.isdir(os.path.join(ROOT,h))][0]
files=[]
for sid in sorted(os.listdir(HOST)):
    d=os.path.join(HOST,sid)
    p=os.path.join(d,"logs","agent.log")
    if os.path.isfile(p): files.append((sid,d,p))
print("agent.log files present:",len(files))
tot=0
for sid,d,p in files:
    n=0
    with open(p,'rb') as f:
        for _ in f: n+=1
    tot+=n
print("total agent.log lines:",tot)
print()
print("=== sample first 3 lines of one agent.log (structure only) ===")
sid,d,p=files[-1]
with open(p,encoding="utf-8",errors="replace") as f:
    for i,ln in enumerate(f):
        if i>=3: break
        print("  ",ln[:220].rstrip())