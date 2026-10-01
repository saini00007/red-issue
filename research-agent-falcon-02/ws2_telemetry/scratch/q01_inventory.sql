\pset border 2
select table_name from information_schema.tables where table_schema='tenant_xbow' order by 1;
select nspname from pg_namespace where nspname not like 'pg\_%' and nspname <> 'information_schema' order by 1;
select 'SCANS_TOTAL', count(*)::text from tenant_xbow.scans;
