select table_name||' | '||column_name||' | '||data_type||coalesce('|enum:'||(
  select string_agg(e.enumlabel,',' order by e.enumsortorder)
  from pg_type t join pg_enum e on e.enumtypid=t.oid
  where t.typname=c.udt_name),'')
from information_schema.columns c
where table_schema='tenant_xbow' and table_name in ('scans','ledger_cell','agent_messages','findings','evidence','chains','scan_ledger_cell')
order by table_name, ordinal_position;
