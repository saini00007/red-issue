import re, subprocess, os, concurrent.futures

BASE = "https://www.infinitycapital.bh"
home = open("tool_outputs/home.html", encoding="utf8", errors="replace").read()
chunks = sorted(set(re.findall(r'/_next/static/chunks/[A-Za-z0-9._/-]+\.js', home)))
chunks += sorted(set(re.findall(r'/_next/static/media/[A-Za-z0-9._/-]+', home)))
os.makedirs("tool_outputs/chunks", exist_ok=True)
print("chunks found:", len(chunks))

def dl(c):
    name = c.split("/")[-1]
    p = "tool_outputs/chunks/" + name
    if os.path.exists(p): return name, 0
    r = subprocess.run(["curl","-sk","--max-time","30","-o",p,"-w","%{http_code}",BASE+c],capture_output=True,text=True)
    return name, r.stdout

with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    for n, c in ex.map(dl, chunks):
        print(c, n)
