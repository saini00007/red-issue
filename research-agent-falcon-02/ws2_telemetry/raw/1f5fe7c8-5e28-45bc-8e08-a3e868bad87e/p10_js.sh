#!/bin/bash
cd $WORK_PATH
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
mkdir -p p10js
echo "=== fetch contact page + all JS chunks ==="
curl -sk -A "$UA" "https://www.infinitycapital.bh/contact" -o p10js/contact.html -w "contact code=%{http_code} size=%{size_download}\n"
python3 - <<'EOF'
import re,urllib.parse
h=open('p10js/contact.html',errors='ignore').read()
srcs=set(re.findall(r'src="([^"]+\.js[^"]*)"',h))
print("chunks found:",len(srcs))
for s in sorted(srcs): print(s)
open('p10js/chunks.txt','w').write("\n".join(sorted(srcs)))
EOF
