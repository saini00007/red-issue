select 'ATTEMPTS_X_FLOORCLAIM', fgrp, attempts::text, count(*)::text from (
  select case when claimed_by like 'floor-%' then 'floor' when claimed_by is null then 'unclaimed' else 'other' end as fgrp,
         attempts
  from tenant_xbow.ledger_cell) t group by fgrp, attempts order by fgrp, attempts::int;
select 'THRASHY_GE3_BY_FLOOR', fgrp, count(*)::text from (
  select case when claimed_by like 'floor-%' then 'floor' when claimed_by is null then 'unclaimed' else 'other' end as fgrp
  from tenant_xbow.ledger_cell where attempts >= 3) t group by fgrp;
select 'AT_CAP_6_BY_FLOOR', fgrp, count(*)::text from (
  select case when claimed_by like 'floor-%' then 'floor' when claimed_by is null then 'unclaimed' else 'other' end as fgrp
  from tenant_xbow.ledger_cell where attempts >= 6) t group by fgrp;
select 'STATE_X_FLOOR', fgrp, state, count(*)::text from (
  select case when claimed_by like 'floor-%' then 'floor' when claimed_by is null then 'unclaimed' else 'other' end as fgrp, state
  from tenant_xbow.ledger_cell) t group by fgrp, state order by fgrp, 3 desc;
select 'CELL_METHODS_FLOOR_STILL_TESTING', count(*)::text from tenant_xbow.ledger_cell
  where state='testing' and claimed_by like 'floor-%' and methods_used::text like '%exploit_floor%';
select 'APPLICABLE_STILL_TESTING', count(*)::text from tenant_xbow.ledger_cell where applicable and state='testing';
select 'UNTESTED_APPLICABLE', count(*)::text from tenant_xbow.ledger_cell where applicable and state='untested';
select 'NA_REASON_TOP', left(coalesce(na_reason,'(null)'),60) as r, count(*)::text
  from tenant_xbow.ledger_cell where state='na' group by r order by 2 desc limit 12;
select 'SCANS_LEDGER_DIST', n::text, count(*)::text from (
  select l.scan_id, count(*) n from tenant_xbow.ledger_cell l group by l.scan_id) t group by t.n order by t.n::int desc;
select 'SCANS_LEDGER_COUNTS', count(distinct scan_id)::text, count(*)::text from tenant_xbow.ledger_cell;
