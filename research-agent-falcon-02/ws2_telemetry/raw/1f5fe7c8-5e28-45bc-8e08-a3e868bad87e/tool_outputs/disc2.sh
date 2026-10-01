#!/bin/bash
# Content discovery: fetch candidate paths slowly (WAF/rate-limit aware) and
# record status + size + title so we can tell real routes from the catch-all.
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
BASE="https://www.infinitycapital.bh"
OUT="$WORK_PATH/tool_outputs/disc2.tsv"
: > "$OUT"
paths=(
 "/" "/investment-portfolio" "/privacy-terms" "/contact" "/about" "/about-us"
 "/services" "/team" "/portfolio" "/news" "/insights" "/blog" "/careers"
 "/api" "/api/send" "/api/contact" "/graphql" "/admin" "/login" "/dashboard"
 "/.env" "/.git/HEAD" "/.git/config" "/robots.txt" "/sitemap.xml"
 "/openapi.json" "/swagger.json" "/api-docs" "/_next/static/"
 "/atom.xml" "/feeds/all.atom.xml" "/404" "/manifest.json"
 "/backup.zip" "/config.json" "/.well-known/security.txt" "/feed.xml"
)
for p in "${paths[@]}"; do
  code=$(curl -s -A "$UA" -H "Accept: text/html,application/xhtml+xml" --max-time 25 \
    -o /tmp/d_body -w "%{http_code}" "$BASE$p")
  sz=$(wc -c < /tmp/d_body)
  title=$(grep -o '<title>[^<]*' /tmp/d_body | head -1 | sed 's/<title>//')
  sig=$(md5sum /tmp/d_body | cut -c1-8)
  printf "%s\t%s\t%s\t%s\t%s\n" "$code" "$sz" "$sig" "$p" "$title" >> "$OUT"
  echo -e "$code\t$sz\t$sig\t$p\t$title"
  sleep 4
done
echo "DONE -> $OUT"
