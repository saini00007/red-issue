\echo ===which-scans-have-graphql-elements===
select i.scan_id::text, count(*) as gql_elements, min(s.started_at)::text
from tenant_xbow.inventory_element i join tenant_xbow.scans s on s.scan_id=i.scan_id
where i.kind='graphql' group by 1,3 order by 3;
\echo ===scans-timeline-last15===
select scan_id::text, status::text, started_at::text, finished_at::text from tenant_xbow.scans order by started_at desc limit 15;
\echo ===graphql-cells-per-scan===
select c.scan_id::text, c.state, count(*), sum(c.attempts), max(c.updated_at)::text
from tenant_xbow.ledger_cell c where c.vuln_class='graphql' group by 1,2 order by 5 desc limit 20;
\echo ===tool_invocations-mentioning-graphql-or-ws===
select count(*) from tenant_xbow.tool_invocations where command ~* 'graphql|/ws|websocket|wscat' ;
\echo ===tool_invocations-per-scan-top===
select scan_id::text, count(*) from tenant_xbow.tool_invocations group by 1 order by 2 desc limit 8;
