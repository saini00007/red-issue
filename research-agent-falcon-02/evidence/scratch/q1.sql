select current_database();
select nspname from pg_namespace where nspname like 'tenant%';
select table_name from information_schema.tables where table_schema='tenant_xbow' order by 1;
