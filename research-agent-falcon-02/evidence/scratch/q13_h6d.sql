\echo ===H6-methods-bloat-from-prompt-free-text===
select
  count(*) as total_method_strings,
  count(*) filter (where length(m) > 120) as longer_than_120c,
  count(*) filter (where length(m) > 400) as longer_than_400c,
  max(length(m)) as longest,
  round(avg(length(m)),1) as avg_len
from tenant_xbow.ledger_cell c, lateral jsonb_array_elements_text(coalesce(c.methods_used,'[]'::jsonb)) m;
\echo ===H6-exploit-floor-vs-llm-methods-split===
select
  count(*) filter (where m like 'exploit_floor:%') as floor_methods,
  count(*) filter (where m not like 'exploit_floor:%') as llm_free_text_methods
from tenant_xbow.ledger_cell c, lateral jsonb_array_elements_text(coalesce(c.methods_used,'[]'::jsonb)) m;
\echo ===H6-methods-array-size===
select jsonb_array_length(coalesce(methods_used,'[]'::jsonb)) as n, count(*) from tenant_xbow.ledger_cell
where jsonb_array_length(coalesce(methods_used,'[]'::jsonb))>0 group by 1 order by 1;
\echo ===H6-skill-gate-relevant-methods-hits===
select count(*) as cells_with_a_required_oracle_named from tenant_xbow.ledger_cell c
where vuln_class='sqli' and exists (select 1 from jsonb_array_elements_text(coalesce(c.methods_used,'[]'::jsonb)) m where m ilike '%sqlmap%');
