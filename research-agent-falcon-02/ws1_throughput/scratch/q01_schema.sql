\pset pager off
select table_name from information_schema.tables where table_schema='tenant_xbow' order by 1;
select column_name||' '||data_type from information_schema.columns where table_schema='tenant_xbow' and table_name='ledger_cell' order by ordinal_position;