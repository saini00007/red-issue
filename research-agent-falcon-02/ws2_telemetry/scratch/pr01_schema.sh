set -u
DB=/home/admin/research/2026-09-29-deepdive/proxy/data/proxy_log.db
echo "=== PROXY DB TABLES (read-only uri) ==="
sqlite3 "file:$DB?mode=ro&immutable=1" ".tables" 2>&1
echo "=== PROXY DB SCHEMA ==="
sqlite3 "file:$DB?mode=ro&immutable=1" ".schema" 2>&1 | head -80