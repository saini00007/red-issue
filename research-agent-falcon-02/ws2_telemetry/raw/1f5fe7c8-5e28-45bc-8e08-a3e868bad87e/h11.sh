#!/bin/bash
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
B=https://www.infinitycapital.bh
echo "### http1.1 headers root"
curl -s -m 25 --http1.1 -D - -o body_h11_root.html -A "$UA" "$B/" | head -30
echo "### http1.1 second request /contact"
curl -s -m 25 --http1.1 -o body_h11_contact.html -w "contact %{http_code} %{size_download}\n" -A "$UA" "$B/contact"
echo "### http1.1 third request /?page=2"
curl -s -m 25 --http1.1 -o body_h11_p2.html -w "p2 %{http_code} %{size_download}\n" -A "$UA" "$B/?page=2"
echo "### http1.1 robots.txt"
curl -s -m 25 --http1.1 -o body_h11_robots.txt -w "robots %{http_code} %{size_download}\n" -A "$UA" "$B/robots.txt"
echo "### default h2 again"
curl -s -m 25 -o /dev/null -w "h2 %{http_code} %{size_download}\n" -A "$UA" "$B/"