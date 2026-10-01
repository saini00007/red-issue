select 'applic_state', applicable, state, count(*) from tenant_xbow.ledger_cell group by 2,3 order by 2,4 desc;
select 'non_na_inapplicable', count(*) from tenant_xbow.ledger_cell where applicable=false and state<>'na';
select 'na_with_methods', count(*) from tenant_xbow.ledger_cell where state='na' and jsonb_array_length(coalesce(methods_used,'[]'::jsonb))>0;
select 'attempted_with_methods', count(*) filter (where jsonb_array_length(coalesce(methods_used,'[]'::jsonb))>0), count(*) from tenant_xbow.ledger_cell where state='attempted';
select 'attempted_progress', count(*) filter (where last_progress > created_at + interval '1 second'), count(*) from tenant_xbow.ledger_cell where state='attempted';
select 'testing_applic_false', count(*) from tenant_xbow.ledger_cell where applicable=false and state='testing';
