\echo ===attempted-cells-na_reason===
select left(coalesce(na_reason,''),80) as r, count(*) from tenant_xbow.ledger_cell
where state='attempted' and attempts=0 group by 1 order by 2 desc;
\echo ===tested_clean-with-no-method===
select count(*) from tenant_xbow.ledger_cell where state='tested_clean' and COALESCE(jsonb_array_length(methods_used),0)=0;
\echo ===confirmed-with-finding-id===
select count(*) filter (where finding_id is not null) as with_fid, count(*) from tenant_xbow.ledger_cell where state='confirmed';
\echo ===graphql-cells-non-na-detail===
select scan_id::text, state, applicable, attempts, COALESCE(jsonb_array_length(methods_used),0) as nmethods, left(coalesce(na_reason,''),40)
from tenant_xbow.ledger_cell where vuln_class='graphql' and state<>'na' order by 1;
\echo ===testing-cells-stuck-with-claim===
select state, count(*) filter (where claimed_by is not null) as claimed from tenant_xbow.ledger_cell where state='testing' group by 1;
