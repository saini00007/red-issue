#!/bin/bash
B=https://www.infinitycapital.bh
sleep 8
curl -sk -D /tmp/h.txt -o /tmp/rb.txt "$B/robots.txt"
echo "--- headers"; cat /tmp/h.txt
echo "--- body size"; wc -c /tmp/rb.txt
echo "--- title"; grep -o '<title>[^<]*' /tmp/rb.txt | head -2
echo "--- first 300"; head -c 300 /tmp/rb.txt
