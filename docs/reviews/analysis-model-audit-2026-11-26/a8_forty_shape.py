"""Audit of Automated Analysis (session 10204): what the engine's own session-361 statistics would say of the forty.

The deep hunt's drafts (all forty of the sheet) carry no `statistics` block: builder.build never calls
findings_common.trend_p or step_or_trend, and no q-value is computed over the round. This runs the engine's own two
functions on each draft's full years (from its CSV) and Benjamini-Hochberg over the 38 yearly claims, to show what a
reader of a weekly-hunt draft would have been told and a reader of these is not.

Run: python runs/a8_forty_shape.py <repo root> > runs/a8.out
"""
import csv
import os
import re
import sys

ROOT = sys.argv[1]
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import findings_common as common  # noqa: E402

SHEET = os.path.join(ROOT, "docs", "reviews", "findings-shortlist-2026-11-19.md")


def main():
    text = open(SHEET, encoding="utf-8").read()
    rows = []
    for m in re.finditer(r"^### (\d+)\. .*?docs/findings/([^ ]+?)\.reproduce\.do", text, re.M | re.S):
        no, slug = int(m.group(1)), m.group(2)
        lines = [ln for ln in open(os.path.join(ROOT, "docs", "findings", slug + ".csv"), encoding="utf-8") if not ln.startswith("#")]
        full = [(int(float(r["year"])), float(r["value"])) for r in csv.DictReader(lines) if str(r.get("full_year")) == "1"]
        if len(full) < 4 or "events/" in slug:
            continue
        ys, vs = [y for y, _ in full], [v for _, v in full]
        sh = common.step_or_trend(ys, vs)
        rows.append([no, slug, len(full), common.trend_p(ys, vs), sh])
    ps = sorted((r[3], i) for i, r in enumerate(rows))
    m = len(ps)
    q = [None] * m
    prev = 1.0
    for rank in range(m, 0, -1):
        p, i = ps[rank - 1]
        prev = min(prev, p * m / rank)
        q[i] = prev
    print("no,slug,full_years,p_trend,q_bh_over_the_forty,step_better,break_year,before,after")
    steps = 0
    for r, qq in zip(rows, q):
        sh = r[4] or {}
        steps += bool(sh.get("step_better"))
        print(f"{r[0]},{r[1]},{r[2]},{r[3]:.6f},{qq:.6f},{sh.get('step_better')},{sh.get('break_year')},{sh.get('before')},{sh.get('after')}")
    print(f"claims {m}; a step fits better than a line: {steps}; q above 0.05: {sum(1 for x in q if x > 0.05)}")


if __name__ == "__main__":
    main()
