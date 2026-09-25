#!/usr/bin/env python3
"""Draw the news-scoring evaluation sample: warehouse/news/eval/eval_sample.csv.

Energy Research Warehouse (ERW). Takes the stories scored in the FIRST scoring
run (the earliest scored_at in warehouse/output/news_stories.csv) and draws 50,
stratified across significance bands and sectors, for a human to score by
hand. eval.py then compares the model with the human.

    python warehouse/news/eval/sample.py            # 50 stories, seed 20260925
    python warehouse/news/eval/sample.py --n 50 --force

Stratification: bands 0-3, 4-6, 7-8, 9-10. Each band gets an equal share of
the sample (rarer bands give their unused share to the others); within a band,
stories are taken round-robin across sectors, so a common sector cannot fill a
band. The draw is seeded, so it is reproducible. The file is not overwritten
once it exists (it holds the human's scores) unless --force is given.

Columns: id, title, url, sector, model_significance, model_ai_power,
human_significance (blank), human_ai_power (blank), notes (blank).
"""

import argparse
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "connectors"))
sys.path.insert(0, os.path.join(HERE, ".."))
import iso_prices as ip  # noqa: E402
from ingest import NAME, NEWS_COLS  # noqa: E402

OUT = os.path.join(HERE, "eval_sample.csv")
BANDS = [(0, 3), (4, 6), (7, 8), (9, 10)]


def draw(scored, n, seed):
    scored = scored.sample(frac=1, random_state=seed)  # shuffle once, reproducibly
    pools = [scored[scored["sig"].between(lo, hi)] for lo, hi in BANDS]
    quota = [0] * len(BANDS)
    left = n
    while left > 0 and any(len(p) > q for p, q in zip(pools, quota)):
        for i, p in enumerate(pools):
            if left > 0 and len(p) > quota[i]:
                quota[i] += 1
                left -= 1
    picked = []
    for p, q in zip(pools, quota):
        by_sector = [g for _, g in p.groupby("sector")]
        k = 0
        while q > 0:  # round-robin: the k-th story of each sector, then the (k+1)-th
            took = False
            for g in by_sector:
                if q > 0 and k < len(g):
                    picked.append(g.iloc[[k]])
                    q -= 1
                    took = True
            if not took:
                break
            k += 1
    return pd.concat(picked) if picked else scored.iloc[0:0]


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW news eval sample")
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--seed", type=int, default=20260925)
    ap.add_argument("--force", action="store_true", help="overwrite an existing sample")
    args = ap.parse_args(argv)
    if os.path.exists(OUT) and not args.force:
        print(f"{OUT} exists (it may hold human scores); use --force to redraw")
        return 2
    df = ip.read_series(os.path.join(ip.OUT_DIR, NAME + ".csv"), NEWS_COLS)
    scored = df[df["scored_at"] != ""].copy()
    if scored.empty:
        print("no scored stories yet; run warehouse/news/score.py first")
        return 2
    first = scored["scored_at"].min()
    scored = scored[scored["scored_at"] == first].copy()
    scored["sig"] = scored["significance"].astype(int)
    s = draw(scored, args.n, args.seed)
    out = pd.DataFrame({
        "id": s["event_id"], "title": s["title"], "url": s["source_url"], "sector": s["sector"],
        "model_significance": s["significance"], "model_ai_power": s["ai_power_relevance"],
        "human_significance": "", "human_ai_power": "", "notes": ""})
    out = out.sort_values(["model_significance", "sector"], key=lambda c: c.astype(str)).reset_index(drop=True)
    out.to_csv(OUT, index=False, lineterminator="\n")
    bands = {f"{lo}-{hi}": int(s["sig"].between(lo, hi).sum()) for lo, hi in BANDS}
    print(f"wrote {os.path.relpath(OUT, ip.ROOT)}: {len(out)} stories from the first scoring run "
          f"({first}; {len(scored)} stories); by band {bands}; sectors {out['sector'].nunique()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
