"""Energy Research Warehouse (ERW), session 148: Ask ERCOT's last seconds, the measured record.

Builds warehouse/chat/eval_ercot_speed_results_148.csv, one row for each of the 100 test questions of session 137
(warehouse/chat/eval_ercot_panel.json), from the lines the runner wrote (site/scripts/eval-ask-speed.mjs):

    python warehouse/chat/eval/ercot_speed_results_148.py \
        --before runs/session143/after_sample.jsonl runs/session143/after_rest.jsonl <before23.jsonl> \
        --after <after100.jsonl> [--reask <reask_*.jsonl> ...] [--summary]

before: the tool as session 143 left it. For 77 questions that is session 143's own record of 7 October 2026 (its
"after" runs); for the 22 it did not ask and the one that failed (h13) it is this session's run of the same tool (the
session's build with every new switch off, the reserve prices by day and month not offered and the pages of a read
asked for one after another), asked on 8 October 2026. A later file is the newer answer and is the one kept.
after: one run of all 100 with the session's changes on. A question asked again with one change switched off (--reask)
is listed under its run's name beside it and never replaces the after answer. A question not asked has empty fields:
nothing is filled in. session 143's record (eval_ercot_speed_results.csv) is not touched.

--summary prints, by kind: the pass counts, the median and the 90th percentile of the seconds to the answer's words,
how many answers are under the targets (5 seconds for a question about numbers, 2 for an idea), the cost, and the
slowest five answers after the changes with where their time went. No request and no model call: it reads files.
"""
import argparse
import csv
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
from ercot_speed_results import KINDS, STAGES, fields, lines, pct  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "chat", "eval_ercot_speed_results_148.csv")
TARGET = {"conceptual": 2.0, "chart": 5.0, "sentence": 5.0, "refuse": 2.0}   # seconds to the words: an idea 2, a number 5
GROUPS = KINDS + ["number (chart and sentence)", "all"]


def in_group(kind, group):
    return group == "all" or kind == group or (group.startswith("number") and kind in ("chart", "sentence"))


def extra(r):
    """What session 148 added to an answer's line: whether a rule wrote the read, and each model call's effort."""
    if r is None:
        return {"after_planned_by": "", "after_plan_shape": "", "after_efforts": ""}
    return {"after_planned_by": r.get("planned_by") or "", "after_plan_shape": r.get("plan_shape") or "", "after_efforts": ";".join(r.get("efforts") or [])}


def where(r):
    """An answer's steps in a few words: each model call with its seconds, each turn of reads with its seconds."""
    out = []
    for s in r.get("steps", []):
        if s.get("what") == "model":
            out.append(f"{s.get('stage')} model {s.get('ms', 0) / 1000:.1f}s" + (f" ({s.get('path')})" if s.get("path") else ""))
        elif s.get("what") == "tools":
            calls = s.get("calls") or []
            out.append(f"reads {s.get('ms', 0) / 1000:.1f}s (" + ", ".join(f"{c.get('table') or c.get('tool')}{' again' if c.get('repeat') else ''}" for c in calls) + ")")
        elif s.get("what") == "rule":
            out.append(f"rule ({s.get('shape')})")
    return "; ".join(out)


def summary(rows, before, after, reasks):
    def col(part, key):
        return [float(r[key]) for r in part if r[key] not in ("", None)]

    for when in ("before", "after"):
        print(f"\n{when.upper()}")
        for group in GROUPS:
            part = [r for r in rows if r[f"{when}_total_ms"] != "" and in_group(r["kind"], group)]
            if not part:
                continue
            words = col(part, f"{when}_seconds_words")
            f = lambda k, p: (lambda v: "none" if v is None else f"{v:.1f}")(pct(col(part, f"{when}_{k}"), p))  # noqa: E731
            med = {s: statistics.median(col(part, f"{when}_{s}_ms")) for s in STAGES}
            print(f"  {group}: n {len(part)}, pass {sum(int(r[f'{when}_pass']) for r in part)}; seconds to the words median / p90 {f('seconds_words', 50)} / {f('seconds_words', 90)}, "
                  f"first sign {f('seconds_first_sign', 50)}, whole {f('seconds', 50)} / {f('seconds', 90)}; under 5 s {sum(1 for x in words if x < 5)}, under 2 s {sum(1 for x in words if x < 2)}; "
                  f"stage medians ms {' '.join(f'{s} {med[s]:.0f}' for s in STAGES)}; mean USD {statistics.mean(col(part, f'{when}_usd')):.4f}, sum USD {sum(col(part, f'{when}_usd')):.4f}; "
                  f"model calls mean {statistics.mean(col(part, f'{when}_model_calls')):.2f}, tool calls mean {statistics.mean(col(part, f'{when}_tool_calls')):.2f}")
    print("\nTHE SAME QUESTIONS, BEFORE AND AFTER (those asked both times)")
    for group in GROUPS:
        part = [r for r in rows if r["before_total_ms"] != "" and r["after_total_ms"] != "" and in_group(r["kind"], group)]
        if not part:
            continue
        b, a = col(part, "before_seconds_words"), col(part, "after_seconds_words")
        faster = sum(1 for r in part if float(r["after_seconds_words"]) < float(r["before_seconds_words"]))
        print(f"  {group}: n {len(part)}; pass {sum(int(r['before_pass']) for r in part)} then {sum(int(r['after_pass']) for r in part)}; words median {pct(b, 50):.1f} then {pct(a, 50):.1f} s, p90 {pct(b, 90):.1f} then {pct(a, 90):.1f}; "
              f"faster {faster} of {len(part)}; USD {sum(col(part, 'before_usd')):.4f} then {sum(col(part, 'after_usd')):.4f}")
    print("\nAFTER, BY WHO WROTE THE READ (questions about numbers)")
    num = [r for r in rows if r["after_total_ms"] != "" and r["kind"] in ("chart", "sentence")]
    for name, part in (("a rule", [r for r in num if r["after_planned_by"] == "rule"]), ("the model", [r for r in num if r["after_planned_by"] != "rule"])):
        if part:
            w = col(part, "after_seconds_words")
            same = [r for r in part if r["before_total_ms"] != ""]
            print(f"  {name}: n {len(part)}, pass {sum(int(r['after_pass']) for r in part)}; words median / p90 {pct(w, 50):.1f} / {pct(w, 90):.1f} s, under 5 s {sum(1 for x in w if x < 5)}; "
                  f"mean USD {statistics.mean(col(part, 'after_usd')):.4f}; the same {len(same)} before: words median {pct(col(same, 'before_seconds_words'), 50):.1f} s, pass {sum(int(r['before_pass']) for r in same)}, mean USD {statistics.mean(col(same, 'before_usd')):.4f}")
    print("\nTARGETS (seconds to the words): a question about numbers under 5, an idea under 2")
    for when in ("before", "after"):
        part = [r for r in rows if r[f"{when}_total_ms"] != ""]
        n = [float(r[f"{when}_seconds_words"]) for r in part if r["kind"] in ("chart", "sentence")]
        c = [float(r[f"{when}_seconds_words"]) for r in part if r["kind"] == "conceptual"]
        x = [float(r[f"{when}_seconds_words"]) for r in part if r["kind"] == "refuse"]
        print(f"  {when}: numbers {sum(1 for v in n if v < 5)} of {len(n)} under 5 s (median {pct(n, 50):.1f}); ideas {sum(1 for v in c if v < 2)} of {len(c)} under 2 s (median {pct(c, 50):.1f}); "
              f"refusals {sum(1 for v in x if v < 2)} of {len(x)} under 2 s (median {pct(x, 50):.1f})")
    print("\nFAILURES")
    for when in ("before", "after"):
        bad = [r for r in rows if str(r[f"{when}_pass"]) == "0"]
        print(f"  {when}: " + ("; ".join(f"{r['id']} ({r[f'{when}_why']})" for r in bad) or "none"))
    not_asked = [r["id"] for r in rows if r["after_total_ms"] == ""]
    print(f"  not asked after ({len(not_asked)}): {' '.join(not_asked) or 'none'}")
    for name, got in reasks:
        print(f"  asked again, {name}: " + "; ".join(f"{i} {'pass' if r['pass'] else 'FAIL ' + '; '.join(r.get('why') or [])} {r.get('seconds_words')} s USD {r['cost_usd']:.4f}" for i, r in got.items()))
    print("\nTHE SLOWEST FIVE AFTER (seconds to the words)")
    for r in sorted((r for r in rows if r["after_total_ms"] != ""), key=lambda r: -float(r["after_seconds_words"]))[:5]:
        a = after[r["id"]]
        print(f"  {r['id']} {r['kind']} {r['after_seconds_words']} s (before {r['before_seconds_words'] or 'not asked'}), pass {r['after_pass']}, {a.get('requests')} model calls, {a.get('tool_calls')} tool calls: {where(a)} | {r['question']}")
    print("\nTHE SLOWEST FIVE BEFORE")
    for r in sorted((r for r in rows if r["before_total_ms"] != ""), key=lambda r: -float(r["before_seconds_words"]))[:5]:
        print(f"  {r['id']} {r['kind']} {r['before_seconds_words']} s, then {r['after_seconds_words'] or 'not asked'} s: {where(before[r['id']])} | {r['question']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", nargs="+", required=True)
    ap.add_argument("--after", nargs="+", required=True)
    ap.add_argument("--reask", nargs="*", default=[])
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--no-write", action="store_true", help="print the summary only")
    a = ap.parse_args()
    with open(os.path.join(ROOT, "warehouse", "chat", "eval_ercot_panel.json"), encoding="utf-8") as f:
        questions = json.load(f)["questions"]
    before, after = lines(a.before), lines(a.after)
    reasks = [(os.path.splitext(os.path.basename(p))[0], lines([p])) for p in a.reask]
    rows = []
    for q in questions:
        again = {name: got[q["id"]] for name, got in reasks if q["id"] in got}
        rows.append({"id": q["id"], "kind": q["kind"], "question": q["q"], **fields("before", before.get(q["id"])), **fields("after", after.get(q["id"])), **extra(after.get(q["id"])),
                     "asked_again": "; ".join(f"{name}: {'pass' if r['pass'] else 'fail'}, {r.get('seconds_words')} s, USD {r['cost_usd']:.4f}" for name, r in again.items())})
    head = [
        "# Energy Research Warehouse (ERW), session 148: Ask ERCOT's last seconds, the 100 test questions of session 137 (warehouse/chat/eval_ercot_panel.json) before and after the session's changes",
        "# Asked on a local build of the site, through its own route (site/scripts/eval-ask-speed.mjs); judged by site/scripts/eval-judge.mjs, one rule a kind, the same before and after; built by warehouse/chat/eval/ercot_speed_results_148.py",
        "# before: the tool as session 143 left it. before_run names the run: after_sample and after_rest are session 143's own record of 7 October 2026 (77 questions); before23 is this session's run of the same tool on 8 October 2026 (the 22 questions session 143 did not ask and h13, which failed there)",
        "# after: one run of all 100 on 8 October 2026 with the session's changes on (after_run names it). after_planned_by rule: the read was written by code, with no reading turn by the model; after_efforts: each model call's role and effort. An empty field: not asked; nothing is filled in",
        "# asked_again: the same question asked once more with one change switched off, by run; it never replaces the after answer",
        "# usd: the model cost of that one answer, as the site's cost ledger records it (site_api_calls, step site_ask_ercot). seconds, taken at the reader's end: first_sign to the first thing shown, words to the answer's words, seconds to the whole answer",
        "# _ms: the server's own record of where the time went: planning, fetching, drawing, writing and other sum to total (site/lib/chat/stages.ts). words_first 1: the words were shown before the whole answer",
    ]
    if not a.no_write:
        with open(OUT, "w", encoding="utf-8", newline="") as f:
            f.write("\n".join(head) + "\n")
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        print(f"{OUT}: {len(rows)} questions, {sum(1 for r in rows if r['before_total_ms'] != '')} asked before, {sum(1 for r in rows if r['after_total_ms'] != '')} asked after")
    if a.summary:
        summary([{k: (str(v) if v != "" else "") for k, v in r.items()} for r in rows], before, after, reasks)


if __name__ == "__main__":
    main()
