select 'evidence_cell_link', (cell_id is not null)::text, count(*) from tenant_xbow.evidence_object group by 2;
select 'evidence_kind', kind, count(*) from tenant_xbow.evidence_object group by 2 order by 3 desc;
select 'findings_per_scan', count(*), count(distinct scan_id), round(avg(n),1), max(n) from (select scan_id, count(*) n from tenant_xbow.findings group by 1) t;
select 'findings_evidence_paths_empty', (jsonb_array_length(coalesce(evidence_paths,'[]'::jsonb))=0)::text, count(*) from tenant_xbow.findings group by 2;
select 'findings_severity', severity, count(*) from tenant_xbow.findings group by 2 order by 3 desc;
