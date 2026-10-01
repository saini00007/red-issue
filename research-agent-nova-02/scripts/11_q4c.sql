select 'findings_evidence_paths_type', coalesce(jsonb_typeof(evidence_paths),'<null>'), count(*) from tenant_xbow.findings group by 2;
select 'findings_evidence_paths_empty', count(*) from tenant_xbow.findings where jsonb_typeof(evidence_paths)='array' and jsonb_array_length(evidence_paths)=0;
select 'findings_dedup_by_scan', count(*) filter (where dedup_hash is null) from tenant_xbow.findings;
