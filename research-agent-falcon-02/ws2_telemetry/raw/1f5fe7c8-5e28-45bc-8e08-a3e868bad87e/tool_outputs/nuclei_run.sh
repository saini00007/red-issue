#!/bin/bash
W=${WORK_PATH:-/work}
cd "$W"
U="https://www.infinitycapital.bh"
echo "=== NUCLEI (severity all, rate-limit 10) ==="
timeout 420 nuclei -u "$U" -severity low,medium,high,critical -rate-limit 10 -bulk-size 2 -timeout 10 -retries 1 -silent -nc 2>&1 | tail -40
echo "=== NUCLEI on known paths ==="
for p in /api/ /_next/image /404 /login /admin /.env /sitemap.xml /api/news /api/posts; do
  echo "--- $p"
  timeout 90 nuclei -u "$U$p" -rate-limit 5 -timeout 10 -retries 1 -silent 2>&1 | head -6
done
echo "NUCLEI_DONE"
