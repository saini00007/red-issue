select 'scan_status', status, count(*) from tenant_xbow.scans group by 2 order by 3 desc;
select 'scan_phase', current_phase, count(*) from tenant_xbow.scans group by 2 order by 3 desc;
select 'scan_mode', mode, count(*) from tenant_xbow.scans group by 2 order by 3 desc;
