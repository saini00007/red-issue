#!/bin/bash
B="https://www.infinitycapital.bh"
O=tool_outputs
IMGURL="https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg"
echo "### dalfox _next/image"
timeout 45 dalfox url "$B/_next/image?url=$IMGURL&w=1080&q=75" --silence --no-color --no-spinner > $O/dalfox_next_image.log 2>&1
tail -6 $O/dalfox_next_image.log
echo "### dalfox 404 / api"
timeout 45 dalfox url "$B/404?search=1" --silence --no-color --no-spinner > $O/dalfox_404.log 2>&1
timeout 45 dalfox url "$B/api/?id=1" --silence --no-color --no-spinner > $O/dalfox_api.log 2>&1
tail -4 $O/dalfox_404.log; tail -4 $O/dalfox_api.log
echo "### nuclei"
timeout 60 nuclei -u "$B" -silent -rate-limit 4 -timeout 6 -retries 0 > $O/nuclei_root.log 2>&1
timeout 60 nuclei -u "$B/api/" -silent -rate-limit 4 -timeout 6 -retries 0 > $O/nuclei_api.log 2>&1
echo "root: $(grep -c . $O/nuclei_root.log) lines"; tail -6 $O/nuclei_root.log
echo "api: $(grep -c . $O/nuclei_api.log) lines"; tail -6 $O/nuclei_api.log
echo "=== DONE ==="
