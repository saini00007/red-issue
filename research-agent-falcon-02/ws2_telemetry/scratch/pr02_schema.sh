set -u
DB=/home/admin/research/2026-09-29-deepdive/proxy/data/proxy_log.db
R="sqlite3 -readonly $DB"
echo "=== SCHEMA of calls ==="
$R "select sql from sqlite_master where type='table';" 2>&1
echo "=== COLUMNS ==="
$R "pragma table_info(calls);" 2>&1
echo "=== ROWCOUNT ==="
$R "select count(*) from calls;" 2>&1
echo "=== INDEXES ==="
$R "select name,sql from sqlite_master where type='index';" 2>&1