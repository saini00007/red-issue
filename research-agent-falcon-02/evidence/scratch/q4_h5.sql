\echo ===H5-newtech-cell-states===
select vuln_class, state, count(*) from tenant_xbow.ledger_cell
where vuln_class in ('graphql','websocket','webhook','rate_limit','ai_prompt_injection','ai_indirect_injection','ai_system_prompt_leak','ai_tool_abuse','ai_rag_leak','protocol')
group by 1,2 order by 1,2;
\echo ===H5-all-classes-state-tally===
select state, count(*) from tenant_xbow.ledger_cell group by 1 order by 2 desc;
\echo ===H5-graphql-cells-with-any-attempt===
select vuln_class, sum(attempts) as attempts, count(*) filter (where attempts>0) as touched, count(*) as total
from tenant_xbow.ledger_cell where vuln_class in ('graphql','websocket','webhook')
group by 1;
\echo ===H5-inventory-ai-endpoints===
select count(*) from tenant_xbow.inventory_element where kind='ai_endpoint';
select kind, count(*) from tenant_xbow.inventory_element group by 1 order by 2 desc limit 15;
\echo ===H5-findings-newtech===
select coalesce(category,'(null)') as cat, count(*) from tenant_xbow.findings
where lower(coalesce(category,'')) ~ 'graphql|websocket|socket|ai_|prompt|rag|mcp' group by 1 order by 2 desc;
\echo ===H5-methods-used-on-graphql-cells===
select m, count(*) from tenant_xbow.ledger_cell c, lateral jsonb_array_elements_text(coalesce(c.methods_used,'[]'::jsonb)) m
where c.vuln_class in ('graphql','websocket','webhook') group by 1 order by 2 desc limit 20;
