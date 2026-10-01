\echo ===methods_used-distribution-ALL-cells===
select m, count(*) from tenant_xbow.ledger_cell c, lateral jsonb_array_elements_text(coalesce(c.methods_used,'[]'::jsonb)) m
group by 1 order by 2 desc;
\echo ===cells-with-ANY-method===
select count(*) filter (where jsonb_array_length(coalesce(methods_used,'[]'::jsonb))>0) as with_methods,
       count(*) as total from tenant_xbow.ledger_cell;
\echo ===evidence_ids-present===
select count(*) filter (where jsonb_array_length(coalesce(evidence_ids,'[]'::jsonb))>0) as with_evidence_ids from tenant_xbow.ledger_cell;
\echo ===na-reasons-top15===
select left(coalesce(na_reason,''),70) as r, count(*) from tenant_xbow.ledger_cell where state='na' group by 1 order by 2 desc;
\echo ===attempts-by-state-for-attempted-cells===
select attempts, count(*) from tenant_xbow.ledger_cell where state='attempted' group by 1 order by 1;
\echo ===distinct-scans-with-any-attempted-graphql-or-ws===
select vuln_class, count(distinct scan_id) from tenant_xbow.ledger_cell where vuln_class in ('graphql','websocket','webhook') and state<>'na' group by 1;
