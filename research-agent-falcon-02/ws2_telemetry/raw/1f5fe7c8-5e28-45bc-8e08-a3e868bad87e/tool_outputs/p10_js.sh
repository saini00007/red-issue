#!/bin/bash
cd $WORK_PATH/tool_outputs
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
mkdir -p p10js && cd p10js
curl -sk -A "$UA" "https://www.infinitycapital.bh/contact" -o contact.html -w "contact code=%{http_code} size=%{size_download}\n"
python3 - <<'EOF'
import re
h=open('contact.html',errors='ignore').read()
print("html len",len(h))
srcs=sorted(set(re.findall(r'src="([^"]+\.js[^"]*)"',h)))
print("chunks:",len(srcs))
open('chunks.txt','w').write("\n".join(srcs))
for s in srcs: print(s)
EOF
