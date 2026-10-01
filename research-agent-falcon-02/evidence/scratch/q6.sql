\echo ===scans-with-graphql-inventory-elements===
select i.scan_id::text, count(*) as gql_elements
from tenant_xbow.inventory_element i where i.kind='graphql' group by i.scan_id;
\echo ===scans-cols===
select column_name from information_schema.columns where table_schema='tenant_xbow' and table_name='scans' order by ordinal_position;
\echo ===recent-scans===
select scan_id::text, status::text, created_at::text from tenant_xbow.scans order by created_at desc limit 12;
\echo ===tool-invocation-graphql-distinct-commands===
select left(command, 90) as cmd, count(*) from tenant_xbow.tool_invocations
where command ~* 'graphql|wscat|websocket' group by 1 order by 2 desc limit 15;
