#!/bin/bash
cd $WORK_PATH/tool_outputs/p10js
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0 Safari/537.36"
i=0
while read -r s; do
  i=$((i+1))
  # unescape %5B %5D
  s2=$(python3 -c "import urllib.parse,sys;print(urllib.parse.unquote(sys.argv[1]))" "$s")
  f=$(echo "$s" | md5sum | cut -c1-8).js
  curl -sk -A "$UA" "https://www.infinitycapital.bh${s2}" -o "$f"
  echo "$f <- $s2 ($(stat -c%s "$f") bytes)"
done < chunks.txt
echo "=== mining ==="
echo "--- /api/ references ---"
grep -ohE '/api/[a-zA-Z0-9_/.\-]*' *.js | sort | uniq -c | sort -rn | head -20
echo "--- fetch( calls ---"
grep -ohE 'fetch\([^)]{0,120}' *.js | sort -u | head -20
echo "--- resend / email keys ---"
grep -ohiE 'resend|RESEND_API_KEY|process\.env\.[A-Z_]+' *.js | sort -u | head -20
