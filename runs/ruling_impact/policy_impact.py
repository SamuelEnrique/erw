"""Session 7618 (portable-laptop): the ruling impact of the three lines marked "Changes a figure" under /policy in
docs/reviews/rulings-for-samuel-2026-11-17.md (branch wip/7560-six-reads).

Line 1: the monitor is held because its tables carry the PUCT's news releases. Counts the PUCT's documents and records,
and what /policy and its monitor view draw in this build (held_keys_policy.json, written by held_keys.mjs from the local
build of wip/7610-fault-rows in the internal view).
Line 2: Virginia's filter shows its own records, not the PJM-wide ones: recomputed from site/data/policy/monitor.json
with the page's own rule (lib/policymonitor.ts: a record passes a state filter when its states hold the state).
Line 3: Michigan's one law among the large-load laws: site/data/siting/large_load_rules.json (state_large_load_laws).
Reads the live set for the documents by source (read-only). No model call. Counts only from the held tables.
"""
import ast
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from live import q  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")


def lst(v):
    if isinstance(v, list):
        return v
    if not v:
        return []
    try:
        return list(ast.literal_eval(v))
    except (ValueError, SyntaxError):
        return [v]


mon = json.loads((ROOT / "site" / "data" / "policy" / "monitor.json").read_text(encoding="utf-8"))
rows = mon["rows"]
print(f"monitor.json: built {mon['built']}, {mon['documents']} documents, {mon['records']} records")

print("\n== line 1: the hold for the PUCT's rows")
docs = q("select source, count(*) from public.events where table_name='policy_actions' group by 1 order by 2 desc")
tot = sum(n for _, n in docs)
puct = sum(n for s, n in docs if s.startswith("puct"))
print(f"policy_actions in the live set: {tot} documents; the PUCT's news releases {puct} ({puct / tot * 100:.1f} percent); by source {dict(docs)}")
reads = q("select source, count(*) from public.events where table_name='policy_reads' group by 1")
print(f"policy_reads: {dict(reads)}")
pr = [r for r in rows if r.get("body") == "PUCT"]
print(f"records of the monitor whose body is the PUCT: {len(pr)} of {len(rows)} ({len(pr) / len(rows) * 100:.1f} percent)")
open_rows = [r for r in rows if (lambda s: s is not None and float(s) >= 5)(r.get("significance"))]
open_puct = [r for r in open_rows if r.get("body") == "PUCT"]
print(f"the view as it opens (significance 5 or more): {len(open_rows)} records shown, the PUCT's {len(open_puct)}: without them {len(open_rows) - len(open_puct)} "
      f"({-len(open_puct) / len(open_rows) * 100:+.1f} percent); 'records held' {len(rows)} to {len(rows) - len(pr)} ({-len(pr) / len(rows) * 100:+.1f} percent)")
hk = json.loads((HERE / "cache" / "held_keys_policy.json").read_text(encoding="utf-8"))
for p, r in hk.items():
    print(f"{p}: checked figures drawn {r['shown']}; held checked figures {len(r['held'])}; drawn 'license needed' {r['text']}")

print("\n== line 2: Virginia's filter")


def sig(r):
    try:
        return float(r.get("significance"))
    except (TypeError, ValueError):
        return -1.0


FOOT = ["DC", "DE", "IL", "IN", "KY", "MD", "MI", "NC", "NJ", "OH", "PA", "TN", "VA", "WV"]   # PJM's 13 states and DC
for label, pool in (("the view as it opens (significance 5 or more, any date: OPEN_FILTERS)", [r for r in rows if sig(r) >= 5]),
                    ("every record (the significance floor lifted)", rows)):
    print(f"-- {label}: {len(pool)} records")
    va = [r for r in pool if "VA" in lst(r.get("states"))]
    pjm = [r for r in pool if "PJM" in [g.upper() for g in lst(r.get("grids"))]]
    pjm_wide = [r for r in pjm if not lst(r.get("states"))]
    pjm_states = Counter(s for r in pjm for s in lst(r.get("states")))
    print(f"records whose states hold VA: {len(va)}")
    print(f"records whose grids hold PJM: {len(pjm)}; naming no state (PJM-wide): {len(pjm_wide)}; naming a state: {len(pjm) - len(pjm_wide)} {dict(pjm_states)}")
    union = {r["id"] for r in va} | {r["id"] for r in pjm_wide}
    print(f"Virginia with the PJM-wide records: {len(union)} ({len(union) - len(va):+d}, {(len(union) - len(va)) / len(va) * 100:+.1f} percent)")
    print("each PJM footprint state's filter, now and with the PJM-wide records:")
    print("  " + "; ".join(f"{s} {len({r['id'] for r in pool if s in lst(r.get('states'))})} to "
                           f"{len({r['id'] for r in pool if s in lst(r.get('states'))} | {r['id'] for r in pjm_wide})}" for s in FOOT))

print("\n== line 3: Michigan among the large-load laws")
ll = json.loads((ROOT / "site" / "data" / "siting" / "large_load_rules.json").read_text(encoding="utf-8"))
laws, held = ll["laws"], ll["held_laws"]
print(f"large_load_rules.json built {ll['built']}: {len(laws)} laws shown, {len(held)} held; counts {ll['counts']}")
mi = [l for l in laws if l.get("state") == "MI"]
for l in mi:
    print(f"  Michigan: {l.get('bill') or l.get('law') or l.get('id')}; status {l.get('status')}; smallest load {l.get('min_mw') or l.get('threshold_mw') or l.get('smallest')}")
states = Counter(l.get("state") for l in laws + held)
print(f"states with a law: {len(states)}; Michigan's laws {states.get('MI', 0)}")
status = Counter(l.get("status") for l in laws)
print(f"laws by status: {dict(status)}")
print(f"without Michigan's: {len(laws) - len(mi)} laws shown ({-len(mi) / len(laws) * 100:+.1f} percent); states with a law {len(states) - (1 if states.get('MI') == len(mi) else 0)}; "
      f"'{mi[0].get('status') if mi else ''}' laws {status.get(mi[0].get('status')) if mi else ''} to {status.get(mi[0].get('status')) - len(mi) if mi else ''}")
