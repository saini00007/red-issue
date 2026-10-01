#!/bin/bash
B=https://www.infinitycapital.bh
echo "== /_next/image legit"
curl -s -o /dev/null -w "%{http_code} %{size_download} %{content_type}\n" "$B/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75"
echo "== /_next/image bad host"
curl -s -o /dev/null -w "%{http_code} %{size_download}\n" "$B/_next/image?url=http%3A%2F%2F127.0.0.1%2F&w=64&q=75"
curl -s "$B/_next/image?url=http%3A%2F%2F127.0.0.1%2F&w=64&q=75" | head -c 300; echo
echo "== /api/send GET"
curl -s -o /dev/null -w "%{http_code} %{size_download}\n" "$B/api/send"
echo "== /api/send POST json {}"
curl -s -X POST -H 'content-type: application/json' -d '{}' -w "\n%{http_code}\n" "$B/api/send" | head -c 600
echo "== /api/send POST contact fields"
curl -s -X POST -H 'content-type: application/json' -d '{"name":"Test","email":"test@example.com","message":"hello"}' -w "\n%{http_code}\n" "$B/api/send" | head -c 800
echo "== buildId"
curl -s -o /dev/null -w "%{http_code}\n" "$B/_next/static/BUILD_ID"
curl -s "$B/_next/static/chunks/webpack-e401313d27ef7f61.js" -o /work/webpack.js -w "webpack %{http_code} %{size_download}\n"
