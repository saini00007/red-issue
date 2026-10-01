set -u
q() { docker exec -i scanner-postgres psql -U scanner -d scanner -X -A -t -c "$1" 2>&1; }
echo "=== SCHEMAS ==="
q "select nspname from pg_namespace where nspname not like 'pg_%' and nspname <> 'information_schema' order by 1;"
echo "=== TABLES ==="
q "select table_schema||'.'||table_name from information_schema.tables where table_type='BASE TABLE' and table_schema not in ('pg_catalog','information_schema') order by 1;"
echo "=== DATABASES ==="
q "select datname from pg_database where not datistemplate order by 1;"