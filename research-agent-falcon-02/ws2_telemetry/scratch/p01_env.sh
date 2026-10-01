set -u
PSQL='docker exec -i scanner-postgres psql -U scanner -d scanner -X -A -F| -t'
echo "=== server ==="
docker exec -i scanner-postgres psql -U scanner -d scanner -X -tAc "select version();" 2>&1
echo "=== schemas ==="
docker exec -i scanner-postgres psql -U scanner -d scanner -X -A -tAc "select nspname from pg_namespace where nspname not like 'pg_%' and nspname <> 'information_schema';" 2>&1
echo "=== tables in tenant_xbow ==="
docker exec -i scanner-postgres psql -U scanner -d scanner -X -A -tAc "select table_name from information_schema.tables where table_schema='tenant_xbow' order by 1;" 2>&1