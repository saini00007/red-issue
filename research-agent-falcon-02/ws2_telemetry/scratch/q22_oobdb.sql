select 'OOB_PER_SCAN', scan_id::text, count(*)::text,
       sum(case when cell_id is null then 1 else 0 end)::text as unlinked,
       sum(case when vuln_class is null then 1 else 0 end)::text as novuln,
       sum(case when coalesce(method,'')='' then 1 else 0 end)::text as nomethod,
       to_char(min(created_at),'MM-DD HH24:MI')::text, to_char(max(fired_at),'MM-DD HH24:MI')::text
  from tenant_xbow.oob_token group by scan_id order by 2 desc limit 15;
select 'OOB_LINKED_VS_UNLINKED', case when cell_id is null then 'unlinked(failed gate)' else 'linked' end, count(*)::text
  from tenant_xbow.oob_token group by 1;
select 'OOB_FINDINGS_VERIFIED_METHOD', verification_method, count(*)::text from tenant_xbow.findings
  where verification_method ilike '%oob%' group by 1;
select 'OOB_FINDINGS_TOTAL', count(*)::text, sum(case when verified then 1 else 0 end)::text
  from tenant_xbow.findings where verification_method ilike '%oob%' or category ilike '%ssrf%' or category ilike '%xxe%';
