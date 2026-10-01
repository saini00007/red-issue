import re,subprocess,os
T="https://www.infinitycapital.bh"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
html=open('/work/c_now.html',encoding='utf-8',errors='ignore').read()
urls=sorted(set(re.findall(r'/_next/static/[^"\']+?\.js',html)))
os.makedirs('/work/js',exist_ok=True)
print(len(urls),"bundles")
for u in urls:
    f='/work/js/'+u.replace('/','_')
    if not os.path.exists(f) or os.path.getsize(f)==0:
        subprocess.run(["curl","-s","-A",UA,T+u,"-o",f])
    print(u, os.path.getsize(f) if os.path.exists(f) else -1)
