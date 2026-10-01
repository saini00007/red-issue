\pset pager off
\timing on
-- cost of the per-wave boundary reads on the live 2915-cell grid
SELECT count(*) FROM ledger_cell WHERE scan_id='84aea81a-7e43-495c-9974-ca064ddd3552'::uuid AND applicable=true AND state IN ('untested','testing');
SELECT count(*) FROM ledger_cell c JOIN inventory_element i ON c.element_id=i.element_id WHERE c.scan_id='84aea81a-7e43-495c-9974-ca064ddd3552'::uuid AND c.applicable=true;
SELECT count(*) FROM ledger_cell WHERE scan_id='84aea81a-7e43-495c-9974-ca064ddd3552'::uuid AND applicable=true AND state='attempted' AND attempts>=6;
SELECT vuln_class, state, count(*) FROM ledger_cell WHERE scan_id='84aea81a-7e43-495c-9974-ca064ddd3552'::uuid AND applicable=true GROUP BY 1,2;