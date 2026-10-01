#!/bin/bash
echo "=== where do 'subjects' come from? (from Contentful CMS data) ==="
curl -sk -A "Mozilla/5.0" https://www.infinitycapital.bh/contact -o /tmp/ct.html
grep -oE '"subjects":\[[^]]*\]' /tmp/ct.html | head -3
grep -oE 'subjects[^,]{0,200}' /tmp/ct.html | head -5
echo "=== addresses / emails in the page (mail recipients) ==="
grep -oE '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' /tmp/ct.html | sort -u | head
echo "=== __next_f payload snippets with to/targets ==="
grep -oE 'targets.{0,200}' /tmp/ct.html | head -3
echo "=== any 'to' recipients config ==="
grep -oE '"to":[^,]{0,120}' /tmp/ct.html | sort -u | head
