select scan_id, count(*) filter (where applicable) app, count(*) filter (where applicable and state in ('confirmed','tested_clean','blocked')) res,
  count(*) filter (where applicable and state='attempted') att, count(*) filter (where applicable and state in ('untested','testing')) opn
from tenant_xbow.ledger_cell where scan_id in ('dbf83a85-9ee8-4420-b344-a43c8d5ee2c5','68a58881-ae3b-4f36-90a9-bf254da13fcb','84aea81a-7e43-495c-9974-ca064ddd3552') group by scan_id;
