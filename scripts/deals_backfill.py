#!/usr/bin/env python3
"""The backfill of the deal and datacenter trackers for days the daily run missed (session 2237, chain 156).

Energy Research Warehouse (ERW). From 26 October to 5 November 2026 the daily run's model steps failed on the API's
spending limit (26 to 30 October) or did not run (31 October to 4 November), so the stories of those days were never
scored, and only scored stories reach the extractors (`docs/reviews/deals-audit-2026-11-06.md`, "Ground" and row A16).
The backfill is therefore three steps, in order: score the days' unscored stories (`warehouse/news/score.py`), then
extract their deals (`warehouse/deals/extract.py`) and facilities (`warehouse/datacenters/extract.py`); each extractor
sends every scored story it has not yet checked, so no story is sent twice.

    python scripts/deals_backfill.py --from 2026-10-27 --to 2026-11-05 --dry-run
        what the backfill would send and cost, read from news_stories, the two checked files and the cost of each
        step's recent runs in run_status.csv; calls no model, writes nothing
    python scripts/deals_backfill.py --from 2026-10-27 --to 2026-11-05 --run
        the data machine only, under the data lock, after the owner approves the estimate: the three steps, each with
        caps sized from the estimate (each step's own lock and cost ledger apply)

The estimate is an estimate: the share of the scored stories that reach each extractor is the share it was on the
days around the gap (the scorer decides the sector and significance), and a call's cost is the median of the step's
last successful runs. Stories the feeds never delivered (no row of news_stories for a day) cannot be backfilled from
here; the dry run counts the days with none.
"""

import argparse
import datetime as dt
import math
import os
import re
import statistics
import subprocess
import sys

import pandas as pd


def _hdr(path):
    """The number of "#" header lines before a table's column row (iso_prices.header_rows: never comment="#")."""
    n = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            n += 1
    return n

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "warehouse", "output")
DEAL_SECTORS = ["deal", "ppa", "capital", "nuclear", "generation", "datacenter_power", "lng", "oil", "gas"]
DEAL_BATCH, DC_BATCH, SCORE_BATCH = 12, 10, 25


def read(path, **kw):
    return pd.read_csv(path, skiprows=_hdr(path), dtype=str, keep_default_na=False, **kw)


def step_costs(status_path):
    """{step: (median USD a call, median USD a story)} from the last ten ok runs of each step."""
    rs = read(status_path)
    out = {}
    for step, conn in (("score", "news_score"), ("deals", "deals"), ("datacenters", "datacenters")):
        r = rs[(rs["connector"] == conn) & (rs["status"] == "ok")].tail(10)
        per_call, per_story = [], []
        for d in r["detail"]:
            usd = re.search(r"cost USD ([\d.]+)", d)
            n = re.search(r"calls (\d+)", d)
            s = re.search(r"stories (?:checked|scored) (\d+)", d)
            if usd and n and int(n.group(1)) > 0 and float(usd.group(1)) > 0:
                per_call.append(float(usd.group(1)) / int(n.group(1)))
                if s and int(s.group(1)) > 0:
                    per_story.append(float(usd.group(1)) / int(s.group(1)))
        out[step] = (statistics.median(per_call) if per_call else None,
                     statistics.median(per_story) if per_story else None, len(per_call))
    return out


def estimate(start, end, out_dir=OUT, root=ROOT):
    news = read(os.path.join(out_dir, "news_stories.csv"),
                usecols=["event_id", "event_date", "sector", "significance", "scored_at", "cluster_id"])
    news["day"] = news["event_date"].str[:10]
    deals_checked = set(read(os.path.join(root, "warehouse", "deals", "checked.csv"))["story_id"])
    dc_checked = set(read(os.path.join(root, "warehouse", "datacenters", "checked.csv"))["story_id"])
    sig = pd.to_numeric(news["significance"], errors="coerce")
    scored = news["scored_at"] != ""
    # the share of scored stories each extractor takes, on the 14 days before the window
    lo = (pd.Timestamp(start) - pd.Timedelta(days=14)).strftime("%Y-%m-%d")
    base = news[scored & (news["day"] >= lo) & (news["day"] < start)]
    deal_share = (base["sector"].isin(DEAL_SECTORS) & (pd.to_numeric(base["significance"], errors="coerce") >= 5)).mean() if len(base) else 0.0
    dc_share = (base["sector"] == "datacenter_power").mean() if len(base) else 0.0
    stories_per_cluster = (base.groupby("cluster_id").size().mean() if len(base) else 1.0)
    days = []
    for day in pd.date_range(start, end, freq="D").strftime("%Y-%m-%d"):
        g = news[news["day"] == day]
        gs = g[g["scored_at"] != ""]
        el_d = gs[gs["sector"].isin(DEAL_SECTORS) & (pd.to_numeric(gs["significance"], errors="coerce") >= 5)]
        el_c = gs[gs["sector"] == "datacenter_power"]
        unscored = int((g["scored_at"] == "").sum())
        days.append({"day": day, "stories": len(g), "unscored": unscored,
                     "deal_unchecked": int((~el_d["event_id"].isin(deals_checked)).sum()),
                     "dc_unchecked": int((~el_c["event_id"].isin(dc_checked)).sum()),
                     "deal_from_unscored": round(unscored * deal_share, 1), "dc_from_unscored": round(unscored * dc_share, 1)})
    return pd.DataFrame(days), {"deal_share": deal_share, "dc_share": dc_share, "stories_per_cluster": stories_per_cluster}


def plan(days, shares, costs):
    unscored = int(days["unscored"].sum())
    deal_st = days["deal_unchecked"].sum() + days["deal_from_unscored"].sum()
    dc_st = days["dc_unchecked"].sum() + days["dc_from_unscored"].sum()
    spc = shares["stories_per_cluster"] or 1.0
    steps = [("score", unscored, math.ceil(unscored / SCORE_BATCH) if unscored else 0),
             ("deals", deal_st, math.ceil(deal_st / spc / DEAL_BATCH) if deal_st else 0),
             ("datacenters", dc_st, math.ceil(dc_st / spc / DC_BATCH) if dc_st else 0)]
    rows = []
    for step, stories, n_calls in steps:
        per_call, per_story, n_runs = costs[step]
        usd = (per_story * stories) if (step == "score" and per_story) else (per_call * n_calls if per_call else None)
        rows.append({"step": step, "stories": round(float(stories), 1), "calls": n_calls,
                     "usd": None if usd is None else round(usd, 2), "from_runs": n_runs})
    return pd.DataFrame(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--from", dest="start", required=True)
    ap.add_argument("--to", dest="end", required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--out-dir", default=OUT, help="where news_stories.csv is read (default warehouse/output)")
    args = ap.parse_args(argv)
    days, shares = estimate(args.start, args.end, args.out_dir)
    costs = step_costs(os.path.join(ROOT, "warehouse", "metadata", "run_status.csv"))
    p = plan(days, shares, costs)
    print(f"The backfill of {args.start} to {args.end} (read {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC)")
    print(days.to_string(index=False))
    print(f"\nshares on the 14 days before: {shares['deal_share']:.3f} of scored stories reach the deal extractor, "
          f"{shares['dc_share']:.3f} the datacenter one; {shares['stories_per_cluster']:.2f} stories a cluster")
    print(p.to_string(index=False))
    total = p["usd"].dropna().sum()
    print(f"\nestimated total: USD {total:.2f} (the daily cap of the scheduled model steps is USD 1.50 a day; the backfill "
          f"needs the owner's approval and a run outside the cap); days with no story at all: "
          f"{', '.join(days.loc[days['stories'] == 0, 'day']) or 'none'}")
    if args.dry_run:
        return 0
    py = sys.executable
    calls_score = int(p.loc[p["step"] == "score", "calls"].iloc[0]) + 2
    n_days = (pd.Timestamp(dt.date.today()) - pd.Timestamp(args.start)).days + 1
    env = dict(os.environ, MAX_STORIES_PER_RUN=str(int(days["unscored"].sum()) + 50), MAX_STORIES_PER_SOURCE="100000")
    for cmd in ([py, "warehouse/news/score.py", "--days", str(n_days), "--max-calls", str(calls_score)],
                [py, "warehouse/deals/extract.py", "--max-calls", str(int(p.loc[p["step"] == "deals", "calls"].iloc[0]) * 2 + 5)],
                [py, "warehouse/datacenters/extract.py", "--max-calls", str(int(p.loc[p["step"] == "datacenters", "calls"].iloc[0]) * 2 + 5)]):
        print("running:", " ".join(cmd[1:]))
        rc = subprocess.call(cmd, cwd=ROOT, env=env)
        print(f"exit={rc}")
        if rc != 0:
            print("the backfill stops here: a step failed; its run log and run_status.csv say why")
            return rc
    return 0


if __name__ == "__main__":
    sys.exit(main())
