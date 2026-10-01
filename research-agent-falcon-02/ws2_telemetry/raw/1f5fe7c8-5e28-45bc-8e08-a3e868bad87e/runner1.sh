#!/bin/bash
OUT=/work/evidence
mkdir -p "$OUT"
NONCE="ICVERIFY-$(cat /proc/sys/kernel/random/uuid 2>/dev/null || echo 12345)-A1"
echo "NONCE=$NONCE" > "$OUT/run1.nonce"
{
echo "NONCE $NONCE"
echo "=== SCRIPT SHA256 ==="
sha256sum /work/runner1.sh
echo "=== 1) GET / ==="
curl -sS -o "$OUT/r1_home.html" -D "$OUT/r1_home.hdr" -w 'HTTP=%{http_code} SIZE=%{size_download}\n' https://www.infinitycapital.bh/
cat "$OUT/r1_home.hdr"
echo "=== 2) OPTIONS /api/send ==="
curl -sS -X OPTIONS -D - -o /dev/null -w 'HTTP=%{http_code}\n' https://www.infinitycapital.bh/api/send
echo "=== 3) POST /api/send empty body ==="
curl -sS -X POST -D "$OUT/r1_api_empty.hdr" -o "$OUT/r1_api_empty.body" -w 'HTTP=%{http_code} SIZE=%{size_download}\n' https://www.infinitycapital.bh/api/send
cat "$OUT/r1_api_empty.hdr"
echo "--- body ---"
cat "$OUT/r1_api_empty.body"
} > "$OUT/r1_out.txt" 2>&1
echo done
