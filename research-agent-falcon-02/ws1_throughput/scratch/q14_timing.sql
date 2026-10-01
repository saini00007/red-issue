\pset pager off
\timing on
SELECT 'A_count_open' k, count(*) v FROM tenant_xbow.ledger_cell WHERE scan_id='84aea81a-7e43-495c-9974-ca064ddd3552'::uuid AND applicable=true AND state IN ('untested','testing');
SELECT 'B_full_join_all_cells' k, count(*) v FROM tenant_xbow.ledger_cell c JOIN tenant_xbow.inventory_element i ON c.element_id=i.element_id WHERE c.scan_id='84aea81a-7e43-495c-9974-ca064ddd3552'::uuid AND c.applicable=true;
SELECT 'C_coverage_counts_groupby' k, count(*) v FROM (SELECT vuln_class,state,count(*) FROM tenant_xbow.ledger_cell WHERE scan_id='84aea81a-7e43-495c-9974-ca064ddd3552'::uuid AND applicable=true GROUP BY 1,2) x;
SELECT 'D_reclaim_scan' k, count(*) v FROM tenant_xbow.ledger_cell WHERE scan_id='84aea81a-7e43-495c-9974-ca064ddd3552'::uuid AND claimed_by IS NOT NULL AND state IN ('untested','testing') AND lease_expires_at IS NOT NULL AND lease_expires_at < now();