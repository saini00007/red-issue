select 'applicable_state', state, count(*), round(100.0*count(*)/sum(count(*)) over (),1) from tenant_xbow.ledger_cell where applicable=true group by 2 order by 3 desc;
select 'terminal_unresolved_attempted', count(*) from tenant_xbow.ledger_cell where applicable=true and state='attempted';
select 'resolved', count(*) from tenant_xbow.ledger_cell where applicable=true and state in ('confirmed','tested_clean','blocked');
select 'open', count(*) from tenant_xbow.ledger_cell where applicable=true and state in ('untested','testing');
select 'pct_terminal_unresolved', round(100.0*count(*) filter (where state='attempted')/nullif(count(*) filter (where state<>'na'),0),1) from tenant_xbow.ledger_cell where applicable=true;
