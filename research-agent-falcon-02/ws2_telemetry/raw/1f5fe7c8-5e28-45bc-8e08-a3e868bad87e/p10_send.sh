#!/bin/bash
B="https://www.infinitycapital.bh"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

echo "### A. JSON body probe"
curl -sk -X POST "$B/api/send" -A "$UA" -H "Content-Type: application/json" \
  -d '{"name":"ic-tester","email":"ic-tester@example.invalid","message":"icmap-001","phone":"+97300000000"}' \
  -D /tmp/s_a.hdr -o /tmp/s_a.txt -w "code=%{http_code} size=%{size_download}\n"
head -1 /tmp/s_a.hdr; head -c 400 /tmp/s_a.txt; echo

echo "### B. form-urlencoded"
curl -sk -X POST "$B/api/send" -A "$UA" \
  -d 'name=ic-tester&email=ic-tester@example.invalid&message=icmap-002&phone=%2B97300000000' \
  -D /tmp/s_b.hdr -o /tmp/s_b.txt -w "code=%{http_code} size=%{size_download}\n"
head -1 /tmp/s_b.hdr; head -c 400 /tmp/s_b.txt; echo

echo "### C. empty body"
curl -sk -X POST "$B/api/send" -A "$UA" -H "Content-Type: application/json" -d '{}' \
  -D /tmp/s_c.hdr -o /tmp/s_c.txt -w "code=%{http_code} size=%{size_download}\n"
head -1 /tmp/s_c.hdr; head -c 400 /tmp/s_c.txt; echo

echo "### D. OPTIONS"
curl -sk -X OPTIONS "$B/api/send" -A "$UA" -D - -o /dev/null -w "code=%{http_code}\n" | head -20
