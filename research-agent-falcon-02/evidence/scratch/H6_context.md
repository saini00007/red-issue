--- H6: how much CONTEXT does one worker actually receive? ---
Measure every context channel that reaches an AgentsRuntime worker turn.
READ-ONLY: file sizes + code reading only.

A) /skills catalog the worker may read (methodology.py:70-88 advertises it)
B) the in-band skills block actually PREPENDED per group (father._skills_block)
C) scan_brief.md (the shared brief every worker reads first)
D) tool schemas shipped to the model
E) the static system prompt

Then: the ceiling a worker could pull in if it read every advertised skill.
