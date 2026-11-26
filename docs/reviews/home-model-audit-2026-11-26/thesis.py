"""Session 10236: what the Thesis Builder computes without a model, restated.

1. The gate on the niche, written again from the owner's rules as site/lib/thesis/niche.ts quotes them (its word lists
   are read from that file as data), set beside the site's own gate (gate_site.json, gate_site.mjs) input by input.
2. The saved runs of 6 October 2026 (the main copy's warehouse/output/thesis_state, version 1): the funnel's counts,
   the landscape and the pipeline restated from each run's funnel rows by the selection rule of the method note;
   what the literal-number check left printed; each run's cost against today's ceilings.
3. The spending guard's constants, read from the code.
Run from the worktree root: <venv python> runs/c10236/thesis.py <main copy warehouse/output>
"""
import json
import os
import re
import sys
import unicodedata

OUT = sys.argv[1]
src = open(os.path.join("site", "lib", "thesis", "niche.ts"), encoding="utf-8").read()


def wordset(name):
    m = re.search(r"const " + name + r" = new Set\(\(([\s\S]*?)\)\.split", src)
    return set(" ".join(re.findall(r'"([^"]*)"', m.group(1))).split())


STOP, SECTOR, SELLS, NOTC = wordset("STOP"), wordset("SECTOR"), wordset("SELLS"), wordset("NOT_A_CUSTOMER")
table = re.findall(r'\{ id: "([a-z_]+)", label: "[^"]+", words: \[([^\]]*)\],\s*suggestions: \[([^\]]*)\] \}', src)
TOPICS = [(i, re.findall(r'"([^"]+)"', w), re.findall(r'"([^"]+)"', s)) for i, w, s in table]
DEFAULTS = re.findall(r'"([^"]+)"', re.search(r"DEFAULT_SUGGESTIONS = \[([\s\S]*?)\];", src).group(1))
EXAMPLES = re.findall(r'"([^"]+)"', re.search(r"NICHE_EXAMPLES = \[([\s\S]*?)\] as const", src).group(1))
PLACE = re.search(r'NICHE_PLACEHOLDER = "For example: ([^"]+)"', src).group(1)
plain = lambda s: re.sub(r"[.;:,!?]+$", "", re.sub(r"\s+", " ", s.lower()).strip())
CURATED = {plain(s) for s in [x for t in TOPICS for x in t[2]] + DEFAULTS + EXAMPLES + [PLACE]}


def words(s):
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).replace("&", " and ")
    s = re.sub(r"\bdata[\s-]*cent(?:er|re)(s?)\b", lambda m: " datacenter" + m.group(1) + " ", s)
    return [w for w in re.split(r"[^a-z0-9]+", s) if w]


def verdict(s):
    """The owner's rules: a curated niche passes; refuse under two content words, or when every content word is a sector
    or market word and no customer is named after a last "for" with something before it; pass when something sold or a
    customer is named; otherwise neither rule speaks (with no model, it passes)."""
    w = words(s)
    content = [x for x in w if x not in STOP]
    cust = []
    if "for" in w:
        at = len(w) - 1 - w[::-1].index("for")
        before = [x for x in w[:at] if x not in STOP]
        after = [x for x in w[at + 1:] if x not in STOP]
        if before and after and any(x not in NOTC for x in after):
            cust = after
    if plain(s) in CURATED:
        return "pass", "curated"
    if len(content) < 2:
        return "refuse", "few_words"
    if all(x in SECTOR for x in content) and not cust:
        return "refuse", "sector_only"
    if any(x in SELLS for x in content):
        return "pass", "sells"
    if cust:
        return "pass", "customer"
    return "unsure", "open"


site = json.load(open(os.path.join("runs", "c10236", "gate_site.json"), encoding="utf-8"))
agree = [r for r in site if verdict(r["input"]) == (r["verdict"], r["why"])]
print(f"THE GATE: {len(agree)} of {len(site)} inputs give the same verdict and reason as the site's gate")
for r in site:
    v = verdict(r["input"])
    if v != (r["verdict"], r["why"]):
        print(f"  differs: {r['input']!r}: restated {v}, site {r['verdict']} {r['why']}")
typed = site[:40]
for r in typed:
    print(f"  {r['input']!r}: {r['verdict']} ({r['why']}); with no model: {'run' if r['ok'] else 'refused'} by {r['by']}, {r['suggestions']} chips")
cur = site[40:]
print(f"  curated niches (the table's chips, the defaults, the examples): {len(cur)}, of which pass: {sum(1 for r in cur if r['ok'])}")
refused_open = [r["input"] for r in typed if r["verdict"] == "unsure"]
print(f"  typed inputs no rule speaks for (the model would be asked; with no model they run): {len(refused_open)}: {refused_open}")

print("\nTHE SAVED RUNS (version 1, 6 October 2026)")
D = os.path.join(OUT, "thesis_state")
order = ["found", "private", "fits", "trend", "pipeline"]
tot_nc, tot_nums = 0, 0
for f in sorted(os.listdir(D)):
    s = json.load(open(os.path.join(D, f), encoding="utf-8"))
    rows = s["funnel"]
    reached = [r["reached"] for r in rows]
    restated = [sum(1 for x in reached if order.index(x) >= k) for k in range(5)]
    page = [st["n"] for st in s["report"]["funnel"]["stages"]]
    eligible = [r for r in rows if r["reached"] in ("trend", "pipeline") and (r.get("score") or 0) >= 60]
    pipe = sum(1 for x in reached if x == "pipeline")
    low = [r for r in rows if r["reached"] == "trend" and (r.get("score") or 0) < 60]
    low_ok = all(("too low" in (r.get("stopped") or "")) or ("under 60" in (r.get("stopped") or "")) for r in low)   # "under 60" before session 142
    land = len(s["report"]["landscape"]["companies"])
    blob = json.dumps(s["report"], ensure_ascii=False)
    nc = re.findall(r"\(not confirmed: ([^)]*)\)", blob)
    nums = sum(len([x for x in n.split(", ") if x]) for n in nc)
    tot_nc += len(nc)
    tot_nums += nums
    print(f"{f[:60]}: cost USD {s['cost']:.4f} ({'over' if s['cost'] > 1.0 else 'under'} today's USD 1.00 a run), {s['calls']} calls, {s['searches']} searches")
    print(f"  funnel restated {restated}; the report's {page}; {'equal' if restated == page else 'DIFFER'}")
    print(f"  landscape {land} (restated {restated[3]}); pipeline {pipe} = min(10, {len(eligible)} tied with confidence >= 60): {pipe == min(10, len(eligible))}; "
          f"tied but under 60 said 'too low': {low_ok} ({len(low)})")
    print(f"  texts printed with '(not confirmed: ...)': {len(nc)}, carrying {nums} numbers no cited source holds, e.g. {nc[:3]}")
print(f"all five runs: {tot_nc} texts print {tot_nums} numbers beside '(not confirmed: ...)'")

print("\nTHE SPENDING GUARD (read from the code)")
run = open(os.path.join("warehouse", "thesis", "run.py"), encoding="utf-8").read()
mig = open(os.path.join("warehouse", "supabase", "migrations", "024_thesis.sql"), encoding="utf-8").read()
nm = open(os.path.join("site", "lib", "thesis", "nicheModel.ts"), encoding="utf-8").read()
ru = float(re.search(r"^RUN_USD = ([\d.]+)", run, re.M).group(1))
du = float(re.search(r"^DAY_USD = ([\d.]+)", run, re.M).group(1))
mu = json.loads(re.search(r"^MARKET_USD = (\{[^}]+\})", run, re.M).group(1).replace("'", '"'))
pd = int(re.search(r"p_per_day integer default (\d+)", mig).group(1))
print(f"a run: USD {ru:.2f}; a UTC day: USD {du:.2f} (counted from thesis_runs.usd); runs a day: {pd} (the database counts); {pd} runs x {ru:.2f} = {pd * ru:.2f}")
print(f"the market run's stage reserves: {mu}; sum {sum(mu.values()):.2f}: a run starts only when that much is left under its ceiling")
print(f"the gate's model call: {re.search(r'GATE_CALLS_PER_HOUR = (\d+)', nm).group(1)} calls an hour on one server instance, {re.search(r'GATE_MAX_TOKENS = (\d+)', src).group(1)} output tokens at most, no retry, 8 s")
print("  a stage that costs more than its reserve is kept (Careful.charge logs and does not stop): the ceiling stops the next stage, not the call")
