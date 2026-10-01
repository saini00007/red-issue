import re, collections, os

RAW = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + r"\raw"
path = os.path.join(RAW, "scan_84aea81a_agent_docker.log")
txt = open(path, encoding="utf-8", errors="replace").read()
lines = txt.splitlines()
print("LINES:", len(lines))

# level distribution
lvl = collections.Counter()
ev = collections.Counter()
for ln in lines:
    m = re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \[(\w+)\s*\] ([\w\.\-]+)", ln)
    if m:
        lvl[m.group(1)] += 1
        ev[m.group(2)] += 1
print("\nLEVELS:", dict(lvl.most_common()))
print("\nTOP 45 LOG EVENTS:")
for e, n in ev.most_common(45):
    print("  %-42s %d" % (e, n))

print("\nWARNING/ERROR EVENTS ONLY:")
for e, n in sorted(((e, n) for e, n in ev.items() if "warn" in e or "error" in e or "fail" in e), key=lambda x: -x[1]):
    print("  %-42s %d" % (e, n))

# taxonomy of model-driver / LLM errors by message text
PATTERNS = [
 ("no_choices", r"no choices"),
 ("empty_assistant", r"empty (?:assistant )?(?:response|content)|empty_llm|blank response"),
 ("rate_429", r"\b429\b|rate limit|Too Many Requests|free-models-per-min"),
 ("context_length", r"context length|maximum context|too many tokens|context_length_exceeded|prompt is too long|max_tokens"),
 ("timeout", r"timeout|timed out|ReadTimeout|asyncio\.TimeoutError"),
 ("max_turns", r"max_turns_exceeded|max_turns"),
 ("provider_error_payload", r"Provider returned error|possible provider error payload"),
 ("internal_500", r"\b500\b|Internal server error"),
 ("bad_gateway", r"\b502\b|Bad Gateway|\b504\b|Gateway"),
 ("invalid_request_400", r"\b400\b|InvalidRequest|invalid_request"),
 ("json_decode", r"JSONDecodeError|Expecting value|json.decoder"),
 ("refusal", r"content_filter|refusal|ResponsibleAIPolicy"),
 ("retry", r"\bretry|retries|backoff"),
 ("stream_abort", r"StreamTerminated|stream.*(?:closed|aborted|incomplete)"),
 ("oob_fail", r"oob.*(?:fail|unreachable|error)"),
 ("floor", r"exploit_floor|floor\."),
 ("budget", r"budget|cost_cap|exceed"),
 ("preempt", r"preempt"),
 ("stuck", r"stuck|no.progress|unproductive"),
]
cnt = collections.Counter()
ex = collections.defaultdict(list)
for ln in lines:
    low = ln.lower()
    for name, pat in PATTERNS:
        if re.search(pat, low):
            cnt[name] += 1
            if len(ex[name]) < 3:
                ex[name].append(ln.strip()[:190])
print("\nMESSAGE-LEVEL TAXONOMY (line counts, overlapping):")
for name, _ in PATTERNS:
    print("  %-24s %5d" % (name, cnt.get(name, 0)))
print("\nEXAMPLES:")
for name, _ in PATTERNS:
    if ex[name]:
        print("--", name)
        for e in ex[name]:
            print("     ", e)
