#!/usr/bin/env python3
"""Draw the deal-extraction evaluation sample: warehouse/deals/eval/eval_sample.csv.

Energy Research Warehouse (ERW), session 15, Task 4.

    python warehouse/deals/eval/sample.py            # 40 deals, stratified by deal_type
    python warehouse/deals/eval/sample.py --n 40 --seed 15

Stratified by deal_type: types are taken in turn (round-robin) and a deal is drawn
at random (fixed seed) from each type still holding one, until n deals are drawn
or the table runs out. Each row carries the extracted fields, the stories' titles
and summaries (from news_stories, so the reader can judge without leaving the file),
and one blank column per field, <field>_ok, for the human to mark:
    1  correct      0  wrong      (blank)  cannot tell or not applicable
A field left empty by the extractor is marked 1 if the stories indeed do not state
it, 0 if they do. is_deal_ok says whether the row is a real, specific transaction;
dedup_ok whether its story links are all about this deal and nothing is split off.
Score a filled file with score.py.
"""

import argparse
import os
import random
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "news"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "deals"))
import iso_prices as ip  # noqa: E402
from ingest import NEWS_COLS  # noqa: E402
from extract import DEAL_COLS  # noqa: E402

FIELDS = ["is_deal", "deal_type", "buyer", "seller", "other_parties", "asset", "technology", "state", "country",
          "mw", "mwh", "dollars", "price", "term_years", "status", "announced_date", "ai_power", "dedup"]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--seed", type=int, default=15)
    ap.add_argument("--out", default=os.path.join(HERE, "eval_sample.csv"))
    args = ap.parse_args(argv)
    deals = ip.read_series(os.path.join(ip.OUT_DIR, "energy_deals.csv"), DEAL_COLS)
    news = ip.read_series(os.path.join(ip.OUT_DIR, "news_stories.csv"), NEWS_COLS).set_index("event_id")
    rng = random.Random(args.seed)
    pools = {t: list(g["event_id"]) for t, g in deals.groupby("deal_type")}
    for p in pools.values():
        rng.shuffle(p)
    picked, types = [], sorted(pools)
    while len(picked) < args.n and any(pools.values()):
        for t in types:
            if pools[t] and len(picked) < args.n:
                picked.append(pools[t].pop())
    rows = []
    for did in picked:
        d = deals.set_index("event_id").loc[did]
        ids = [x for x in d["story_ids"].split(";") if x]
        titles = " || ".join(news.loc[i, "title"] for i in ids if i in news.index)
        summaries = " || ".join(news.loc[i, "summary"] for i in ids if i in news.index)
        row = {"deal_id": did, "event_date": d["event_date"], "deal_type": d["deal_type"], "buyer": d["buyer"],
               "seller": d["seller"], "other_parties": d["other_parties"], "asset": d["asset"],
               "technology": d["technology"], "state": d["state"], "country": d["country"], "mw": d["mw"],
               "mwh": d["mwh"], "dollars": d["dollars"],
               "price": f"{d['price_value']} {d['price_unit']}".strip(), "term_years": d["term_years"],
               "status": d["status"], "announced_date": d["announced_date"], "ai_power": d["ai_power"],
               "confidence": d["confidence"], "n_stories": d["n_stories"], "story_urls": d["story_urls"],
               "story_titles": titles, "story_summaries": summaries}
        row.update({f"{f}_ok": "" for f in FIELDS})
        row["notes"] = ""
        rows.append(row)
    out = pd.DataFrame(rows)
    out.to_csv(args.out, index=False, lineterminator="\n")
    counts = out["deal_type"].value_counts().to_dict()
    print(f"wrote {os.path.relpath(args.out, ROOT)}: {len(out)} deals of {len(deals)} "
          f"({'all of them' if len(out) == len(deals) else 'a stratified sample'}); by type {counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
