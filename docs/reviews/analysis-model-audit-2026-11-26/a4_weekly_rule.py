"""Audit of Automated Analysis (session 10204): the weekly rule re-done from its own files.

For each week under docs/analysis/: the chosen measure, its finding, its score; how many measures competed and their
scores (results.json); and the score re-done by hand from the history the chart file carries, ranked among the last
104 earlier changes as the note says. Prints the keys first so the structure is on record.

Run: python runs/a4_weekly_rule.py <repo root> > runs/a4.out
"""
import glob
import json
import os
import sys

ROOT = sys.argv[1]


def main():
    for wk in sorted(glob.glob(os.path.join(ROOT, "docs", "analysis", "2026-W*"))):
        name = os.path.basename(wk)
        cw = os.path.join(wk, "chart_of_the_week.json")
        rs = os.path.join(wk, "results.json")
        if not os.path.exists(cw):
            print(name, "no chart file")
            continue
        c = json.load(open(cw, encoding="utf-8"))
        print("==", name, "keys:", sorted(c.keys()))
        for k in ("template", "label", "how_picked", "rule", "score", "finding", "caption", "z", "rank", "period", "headline"):
            if k in c:
                v = c[k]
                print(f"  {k}: {json.dumps(v)[:400]}")
        if os.path.exists(rs):
            r = json.load(open(rs, encoding="utf-8"))
            items = r if isinstance(r, list) else r.get("results", r.get("templates", []))
            if isinstance(items, dict):
                items = list(items.values())
            scores = []
            for it in items:
                if not isinstance(it, dict):
                    continue
                sc = it.get("change_score")
                if it.get("about") != "system" or not it.get("new_this_week"):
                    sc = None
                scores.append((sc, it.get("template") or it.get("id") or it.get("label"), it.get("earlier_changes"), it.get("compare")))
            print(f"  results: {len(scores)} entries; with a score: {sum(1 for s in scores if s[0] is not None)}")
            for s in sorted([s for s in scores if s[0] is not None], key=lambda x: -float(x[0]))[:8]:
                print("   ", s)
        # the score again by hand from the chart's own series, where it carries one
        h = c.get("headline") or {}
        hist = h.get("history") if isinstance(h, dict) else None
        if hist:
            seq = [(p, float(v)) for p, v in hist if v is not None] + [(h["period"], float(h["value"]))]
            deltas = [b[1] - a[1] for a, b in zip(seq, seq[1:])]
            d = deltas[-1]
            for win in (104, 102):
                earlier = deltas[:-1][-win:]
                sc = 100.0 * sum(1 for x in earlier if abs(x) < abs(d)) / len(earlier)
                big = sum(1 for x in earlier if abs(x) >= abs(d))
                print(f"  by hand, window {win}: {len(earlier)} earlier changes, score {sc:.2f}, as large {big}, delta {d:.4f}, prev {seq[-2]}")
            print(f"  history points in the chart file: {len(seq)}")


if __name__ == "__main__":
    main()
