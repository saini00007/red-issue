import os, re, collections
ROOT="/var/lib/scanner"
HOST=[os.path.join(ROOT,h) for h in sorted(os.listdir(ROOT)) if os.path.isdir(os.path.join(ROOT,h))][0]
# 1) raw shape of a tool.started / tool.done pair (values redacted)
for sid in sorted(os.listdir(HOST))[:1]:
    pass
files=[]
for sid in sorted(os.listdir(HOST)):
    d=os.path.join(HOST,sid); p=os.path.join(d,"logs","agent.log")
    if os.path.isfile(p): files.append((sid,p))
sid,p=files[-1]
print("=== RAW SHAPE: tool.started and tool.done (endpoint values redacted) ===")
n=0
for ln in open(p,encoding="utf-8",errors="replace"):
    if "event_type=tool." in ln:
        r=re.sub(r'command=\S+','command=<CMD>',ln.rstrip())
        r=re.sub(r'endpoint=\S+','endpoint=<EP>',r)
        r=re.sub(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}','<uuid>',r)
        r=re.sub(r'\S+=[^ ]*[0-9a-f]{16,}\S*','<redacted>=<t>',r)
        print("  ",r[:250]); n+=1
    if n>=4: break