select (cell_id is not null)::text, (finding_id is not null)::text, count(*) from tenant_xbow.evidence_object group by 1,2;
select count(*) from tenant_xbow.evidence_object;
