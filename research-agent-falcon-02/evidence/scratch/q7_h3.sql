\echo ===tool_invocations-columns===
select column_name from information_schema.columns where table_schema='tenant_xbow' and table_name='tool_invocations' order by ordinal_position;
\echo ===tool-distribution-top40===
select tool, count(*) from tenant_xbow.tool_invocations group by 1 order by 2 desc;
\echo ===chain-floor-tool-invocations===
select tool, count(*) from tenant_xbow.tool_invocations where tool like '%chain%' or tool like '%graphql%' or tool like '%channel%' or tool like '%ws%' group by 1;
\echo ===chain_node-capabilities===
select capability, count(*) from tenant_xbow.chain_node group by 1 order by 2 desc;
\echo ===chain_node-attrs-has-proof===
select count(*) as nodes, count(*) filter (where attrs ? 'proof_of_concept') as with_poc,
       count(*) filter (where nullif(attrs->>'evidence_path','') is not null) as with_evpath
from tenant_xbow.chain_node;
\echo ===chain_edge-count===
select count(*) from tenant_xbow.chain_edge;
\echo ===findings-verification-methods===
select verification_method, count(*) from tenant_xbow.findings group by 1 order by 2 desc;
\echo ===executed-chain-findings===
select count(*) from tenant_xbow.findings where verification_method='executed_chain' or category='executed_chain';
