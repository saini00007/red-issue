#!/bin/bash
# Control test: does the /_next/image optimizer accept the site's own referenced
# remote image host (proving the 400 above is an allowlist restriction, not a block)?
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
BASE="https://www.infinitycapital.bh/_next/image"
probe() {
  local label="$1"; local payload="$2"
  local out
  out=$(curl -s -A "$UA" -o "$WORK_PATH/tool_outputs/ctl_$label" -D "$WORK_PATH/tool_outputs/ctlhdr_$label" -w "%{http_code}|%{size_download}|%{content_type}" --max-time 30 -G --data-urlencode "url=$payload" --data "w=256" "$BASE")
  echo "[$label] -> $out"
  echo "   body(first 160): $(head -c 160 "$WORK_PATH/tool_outputs/ctl_$label" | tr -d '\n')"
  sleep 4
}
# host the app itself loads images from
probe "ctf1" "https://images.ctfassets.net/yts1dx0j7jj5/yRvqRHKqEsbLvrma0OXqV/4b64635f8f18ab2e546275054/Ahmed_Taleb_updated-min.jpg"
# non-image extension on same allowlisted host
probe "ctf2" "https://images.ctfassets.net/yts1dx0j7jj5/yRvqRHKqEsbLvrma0OXqV/4b64635f8f18ab2e546275054/image.png"
# bare metadata endpoint on allowlisted host
probe "ctf3" "https://images.ctfassets.net/"
