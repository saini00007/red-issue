set -u
echo "USER=$(whoami)"
echo "HOST=$(hostname)"
for t in sqlite3 python3 python jq; do
  p=$(command -v $t 2>/dev/null || echo MISSING)
  echo "HOSTTOOL $t=$p"
done
echo "--- container logging-proxy ---"
docker exec logging-proxy sh -c 'for t in sqlite3 python3 python; do command -v $t 2>/dev/null || echo "MISSING $t"; done' 2>&1
echo "--- psql check ---"
docker exec scanner-postgres psql -U scanner -d scanner -tAc "select version();" 2>&1 | head -3