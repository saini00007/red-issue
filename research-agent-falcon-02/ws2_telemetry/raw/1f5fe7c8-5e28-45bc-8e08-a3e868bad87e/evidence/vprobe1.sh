#!/bin/bash
# Independent verification probe - Infinity Capital /api/send
OUT=/work/evidence
mkdir -p "$OUT"
{
echo "### nonce: $(cat /proc/sys/kernel/random/uuid)"
echo "### curl: $(curl --version | head -1)"
echo
echo "=== 1) GET / (homepage) ==="
curl -sS -o "$OUT/r1_home.html" -D "$OUT/r1_home.hdr" \
  -w 'HTTP=%{http_code} SIZE=%{size_download}\n' https://www.infinitycapital.bh/
cat "$OUT/r1_home.hdr"
echo
echo "=== 2) OPTIONS /api/send ==="
curl -sS -X OPTIONS -D - -o /dev/null -w 'HTTP=%{http_code}\n' https://www.infinitycapital.bh/api/send
echo
echo "=== 3) POST /api/send with EMPTY body (baseline) ==="
curl -sS -X POST -D "$OUT/r1_api_empty.hdr" -o "$OUT/r1_api_empty.body" \
  -w 'HTTP=%{http_code} SIZE=%{size_download}\n' https://www.infinitycapital.bh/api/send
cat "$OUT/r1_api_empty.hdr"
echo "--- body ---"
cat "$OUT/r1_api_empty.body"
echo
echo "=== 4) GET /api/send (method probe) ==="
curl -sS -X GET -o /dev/null -w 'HTTP=%{http_code}\n' https://www.infinitycapital.bh/api/send
} > "$OUT/r1_out.txt" 2>&1
echo "WROTE $OUT/r1_out.txt"
