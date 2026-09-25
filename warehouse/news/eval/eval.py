#!/usr/bin/env python3
"""Compare the model's news scores with a human's: the ERW scoring benchmark.

Energy Research Warehouse (ERW). Reads warehouse/news/eval/eval_sample.csv
once the human has filled human_significance and human_ai_power, and reports
for both scores:
  - mean absolute error (model minus human, in rubric points)
  - Spearman rank correlation
  - top-10 overlap: of the 10 stories the human ranks highest, how many the
    model also ranks in its top 10 (ties broken by the other score, then id)

    python warehouse/news/eval/eval.py
    python warehouse/news/eval/eval.py --json

Rows without a human score are left out and counted. Exit 2 when no row has
a human score yet. pandas only: Spearman is the Pearson correlation of
average ranks, computed here.
"""

import argparse
import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLE = os.path.join(HERE, "eval_sample.csv")


def spearman(a, b):
    ra, rb = a.rank(method="average"), b.rank(method="average")
    if ra.std() == 0 or rb.std() == 0:
        return float("nan")
    return float(ra.corr(rb))


def top_overlap(df, model_col, human_col, other_model, other_human, k=10):
    k = min(k, len(df))
    m = df.sort_values([model_col, other_model, "id"], ascending=[False, False, True]).head(k)
    h = df.sort_values([human_col, other_human, "id"], ascending=[False, False, True]).head(k)
    return len(set(m["id"]) & set(h["id"])), k


def report(df):
    out = {"rows": int(len(df))}
    for name, mc, hc, om, oh in (
        ("significance", "model_significance", "human_significance", "model_ai_power", "human_ai_power"),
        ("ai_power_relevance", "model_ai_power", "human_ai_power", "model_significance", "human_significance"),
    ):
        both = df.dropna(subset=[mc, hc])
        if both.empty:
            out[name] = {"n": 0}
            continue
        ov, k = top_overlap(both.fillna({om: -1, oh: -1}), mc, hc, om, oh)
        out[name] = {"n": int(len(both)),
                     "mae": round(float((both[mc] - both[hc]).abs().mean()), 3),
                     "bias_model_minus_human": round(float((both[mc] - both[hc]).mean()), 3),
                     "spearman": round(spearman(both[mc], both[hc]), 3),
                     "top10_overlap": f"{ov}/{k}"}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW news scoring benchmark")
    ap.add_argument("--sample", default=SAMPLE)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    if not os.path.exists(args.sample):
        print(f"{args.sample} not found; draw it with warehouse/news/eval/sample.py")
        return 2
    df = pd.read_csv(args.sample, dtype={"id": str})
    for c in ("model_significance", "model_ai_power", "human_significance", "human_ai_power"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    filled = df.dropna(subset=["human_significance", "human_ai_power"], how="all")
    if filled.empty:
        print(f"no human scores yet in {args.sample}: fill human_significance and human_ai_power (0 to 10)")
        return 2
    bad = filled[(filled[["human_significance", "human_ai_power"]] < 0).any(axis=1)
                 | (filled[["human_significance", "human_ai_power"]] > 10).any(axis=1)]
    if len(bad):
        print(f"human scores outside 0 to 10 in rows: {list(bad['id'])}")
        return 2
    r = report(filled)
    r["unscored_rows"] = int(len(df) - len(filled))
    if args.json:
        print(json.dumps(r, indent=2))
        return 0
    print(f"ERW news scoring benchmark: {r['rows']} stories with a human score "
          f"({r['unscored_rows']} not yet scored)")
    for name in ("significance", "ai_power_relevance"):
        m = r[name]
        if not m.get("n"):
            print(f"  {name}: no human scores")
            continue
        print(f"  {name}: n={m['n']}  MAE={m['mae']}  bias={m['bias_model_minus_human']:+}  "
              f"Spearman={m['spearman']}  top-10 overlap={m['top10_overlap']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
