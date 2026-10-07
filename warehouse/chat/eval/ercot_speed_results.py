"""Energy Research Warehouse (ERW), session 143: Ask ERCOT's speed, the measured record.

Builds warehouse/chat/eval_ercot_speed_results.csv, one row for each of the 100 test questions of session 137
(warehouse/chat/eval_ercot_panel.json), from the lines the runner wrote (site/scripts/eval-ask-speed.mjs):

    python warehouse/chat/eval/ercot_speed_results.py --before runs/session143/before_sample.jsonl \
        --after runs/session143/after_sample.jsonl runs/session143/after_rest.jsonl [--summary]

before_*: the tool as it stood at the start of session 143 (with the stage timings added and nothing else changed),
asked on a sample of 20 questions, five of each kind. after_*: the changed tool; a question asked more than once after
the change keeps its newest answer. A question not asked has empty fields: nothing is filled in. s137_*: the same
question's newest answer in session 137's record (eval_ercot_panel_results.csv), the tool as it stood then, for the
before figures of the 80 questions not in today's sample (its seconds are to the whole answer; it has no stages).

--summary prints, by kind, the pass counts, the median and 90th percentile of the seconds to the first sign, to the
answer's words and to the whole answer, the median of each stage, and the mean cost, before and after. No request and
no model call: it reads files.
"""
import argparse
import csv
import io
import json
import os
import statistics

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(ROOT, "warehouse", "chat", "eval_ercot_speed_results.csv")
STAGES = ["planning", "fetching", "drawing", "writing", "other"]
KINDS = ["conceptual", "chart", "sentence", "refuse"]


def lines(paths):
    got = {}
    for p in paths:
        with open(p, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    got[r["id"]] = r          # a later file, or a later line, is the newer answer
    return got


def pct(values, p):
    """The percentile by linear interpolation (numpy's default), or None for no values."""
    v = sorted(values)
    if not v:
        return None
    pos = (len(v) - 1) * p / 100
    lo = int(pos)
    hi = min(lo + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (pos - lo)


def fields(when, r):
    if r is None:
        return {f"{when}_{k}": "" for k in ["run", "pass", "status", "form", "usd", "seconds_first_sign", "seconds_words", "seconds", "words_first", "withdrawn", "retried", "tool_calls", "model_calls"]
                + [f"{s}_ms" for s in STAGES] + ["total_ms", "models", "why"]}
    st = r.get("stages_ms") or {}
    return {
        f"{when}_run": r.get("run", ""), f"{when}_pass": int(bool(r["pass"])), f"{when}_status": r.get("status") or "", f"{when}_form": r.get("form") or "",
        f"{when}_usd": f"{r['cost_usd']:.4f}", f"{when}_seconds_first_sign": r.get("seconds_first_sign", ""), f"{when}_seconds_words": r.get("seconds_words", ""), f"{when}_seconds": r.get("seconds", ""),
        f"{when}_words_first": int(bool(r.get("words_first"))), f"{when}_withdrawn": r.get("withdrawn", 0), f"{when}_retried": int(bool(r.get("retried"))),
        f"{when}_tool_calls": r.get("tool_calls") if r.get("tool_calls") is not None else "", f"{when}_model_calls": r.get("requests") if r.get("requests") is not None else "",
        **{f"{when}_{s}_ms": st.get(s, "") for s in STAGES}, f"{when}_total_ms": st.get("total", ""),
        f"{when}_models": ";".join(sorted({str(s.get("model")) for s in r.get("steps", []) if s.get("what") == "model"})), f"{when}_why": "; ".join(r.get("why") or []),
    }


def summary(rows):
    def col(part, key):
        return [float(r[key]) for r in part if r[key] not in ("", None)]
    for when in ("before", "after"):
        print(f"\n{when.upper()}")
        for kind in KINDS + ["number (chart and sentence)", "all"]:
            part = [r for r in rows if r[f"{when}_total_ms"] != "" and (kind == "all" or r["kind"] == kind or (kind.startswith("number") and r["kind"] in ("chart", "sentence")))]
            if not part:
                continue
            f = lambda k, p: (lambda v: "none" if v is None else f"{v:.1f}")(pct(col(part, f"{when}_{k}"), p))
            med = {s: statistics.median(col(part, f"{when}_{s}_ms")) for s in STAGES}
            print(f"  {kind}: n {len(part)}, pass {sum(int(r[f'{when}_pass']) for r in part)}; seconds median / p90: first sign {f('seconds_first_sign', 50)} / {f('seconds_first_sign', 90)}, "
                  f"words {f('seconds_words', 50)} / {f('seconds_words', 90)}, whole {f('seconds', 50)} / {f('seconds', 90)}; "
                  f"under 5 s to the words {sum(1 for x in col(part, f'{when}_seconds_words') if x < 5)}, under 2 s {sum(1 for x in col(part, f'{when}_seconds_words') if x < 2)}; "
                  f"stage medians ms {' '.join(f'{s} {med[s]:.0f}' for s in STAGES)}; stage means ms {' '.join(f'{s} {statistics.mean(col(part, f'{when}_{s}_ms')):.0f}' for s in STAGES)}; "
                  f"mean USD {statistics.mean(col(part, f'{when}_usd')):.4f}, sum USD {sum(col(part, f'{when}_usd')):.4f}; tool calls mean {statistics.mean(col(part, f'{when}_tool_calls')):.2f}, model calls mean {statistics.mean(col(part, f'{when}_model_calls')):.2f}")
    part = [r for r in rows if r["s137_after_seconds"] != ""]
    print("\nSESSION 137's record (the tool as it stood then), by kind: n, pass, median and p90 seconds to the whole answer, mean USD")
    for kind in KINDS:
        k = [r for r in part if r["kind"] == kind]
        s = [float(r["s137_after_seconds"]) for r in k]
        print(f"  {kind}: n {len(k)}, pass {sum(int(r['s137_after_pass']) for r in k)}, {pct(s, 50):.1f} / {pct(s, 90):.1f} s, USD {statistics.mean(float(r['s137_after_usd']) for r in k):.4f}")
    not_asked = [r["id"] for r in rows if r["after_total_ms"] == ""]
    print(f"\nnot asked after the change ({len(not_asked)}): {' '.join(not_asked)}")
    print("failures after: " + ("; ".join(f"{r['id']} ({r['after_why']})" for r in rows if r["after_pass"] == "0" or r["after_pass"] == 0) or "none"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", nargs="+", required=True)
    ap.add_argument("--after", nargs="+", required=True)
    ap.add_argument("--summary", action="store_true")
    a = ap.parse_args()
    questions = json.load(open(os.path.join(ROOT, "warehouse", "chat", "eval_ercot_panel.json"), encoding="utf-8"))["questions"]
    before, after = lines(a.before), lines(a.after)
    with open(os.path.join(ROOT, "warehouse", "chat", "eval_ercot_panel_results.csv"), encoding="utf-8") as f:
        s137 = {r["id"]: r for r in csv.DictReader(io.StringIO("".join(l for l in f if not l.startswith("#"))))}
    rows = []
    for q in questions:
        old = s137.get(q["id"], {})
        rows.append({"id": q["id"], "kind": q["kind"], "question": q["q"],
                     "s137_after_pass": old.get("after_pass", ""), "s137_after_usd": old.get("after_usd", ""), "s137_after_seconds": old.get("after_seconds", ""), "s137_after_tool_calls": old.get("after_tool_calls", ""),
                     **fields("before", before.get(q["id"])), **fields("after", after.get(q["id"]))})
    head = [
        "# Energy Research Warehouse (ERW), session 143: Ask ERCOT's speed, the 100 test questions of session 137 (warehouse/chat/eval_ercot_panel.json) before and after the session's changes",
        "# Asked on 7 October 2026 on a local build of the site, through its own route (site/scripts/eval-ask-speed.mjs); judged by site/scripts/eval-judge.mjs, one rule a kind, the same before and after; built by warehouse/chat/eval/ercot_speed_results.py",
        "# before: the tool as it stood at the start of the session, on a sample of 20 questions (five of each kind). after: the changed tool. An empty field: the question was not asked in that run; nothing is filled in",
        "# s137_after: the same question's newest answer in session 137's record of 6 October 2026 (eval_ercot_panel_results.csv): the tool as it stood then; its seconds are to the whole answer",
        "# usd: the model cost of that one answer, as the site's cost ledger records it (site_api_calls, step site_ask_ercot). seconds, taken at the reader's end: first_sign to the first thing shown, words to the answer's words, seconds to the whole answer",
        "# _ms: the server's own record of where the time went: planning, fetching, drawing, writing and other sum to total (site/lib/chat/stages.ts). words_first 1: the words were shown before the whole answer",
    ]
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(head) + "\n")
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"{OUT}: {len(rows)} questions, {sum(1 for r in rows if r['before_total_ms'] != '')} asked before, {sum(1 for r in rows if r['after_total_ms'] != '')} asked after")
    if a.summary:
        summary([{k: (str(v) if v != "" else "") for k, v in r.items()} for r in rows])


if __name__ == "__main__":
    main()
