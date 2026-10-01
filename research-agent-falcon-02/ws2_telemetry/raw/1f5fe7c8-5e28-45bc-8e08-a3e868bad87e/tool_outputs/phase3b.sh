#!/bin/bash
B="https://www.infinitycapital.bh"
O=tool_outputs
IMGURL="https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg"
echo "### dalfox _next/image"
timeout 60 dalfox url "$B/_next/image?url=$IMGURL&w=1080&q=75" --silence --no-color --no-spinner 2>&1 | tail -8
echo "### dalfox 404"
timeout 60 dalfox url "$B/404?search=1" --silence --no-color --no-spinner 2>&1 | tail -8
echo "### dalfox api"
timeout 60 dalfox url "$B/api/?id=1" --silence --no-color --no-spinner 2>&1 | tail -8
echo "### nuclei cves"
timeout 90 nuclei -u "$B" -silent -rate-limit 5 -timeout 8 -retries 0 2>&1 | tail -10
echo "### nuclei on 4 known paths"
for p in "/api/" "/404" "/_next/image" "/atom.xml"; do
  echo "-- $p"; timeout 40 nuclei -u "$B$p" -silent -rate-limit 3 -timeout 8 -retries 0 2>&1 | tail -3
done
echo "### nikto"
timeout 90 nikto -h "$B" -nointeractive -Tuning 12 2>&1 | tail -12
echo "=== DONE ==="
