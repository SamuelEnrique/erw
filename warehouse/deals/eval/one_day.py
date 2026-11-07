#!/usr/bin/env python3
"""The daily run's deals and datacenters steps on one stored day, end to end, offline (session 2237, chain 156).

Energy Research Warehouse (ERW). Copies the warehouse's tables as they stand (`energy_deals`, its evidence,
`datacenter_projects`, its evidence, `news_stories`) into a temporary folder, marks the chosen day's eligible stories
as not yet checked, and runs the two extractors with the new code there, so the day is extracted again against every
deal and facility already held (the reference lists, the deduplication, the upgrade of the old columns). The real model
is called under a cap and every call's cost is printed; nothing is written to `warehouse/output` and no ledger row is
written (a code machine). The rows the day produced are written to the folder given as --keep for reading.

    python warehouse/deals/eval/one_day.py --day 2026-11-05 --cap 1.00 --keep runs/s2237
"""

import argparse
import importlib.util
import os
import shutil
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

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "warehouse", "deals"))
import fixture as dfx  # noqa: E402

_spec = importlib.util.spec_from_file_location("erw_dc_fixture_1d", os.path.join(ROOT, "warehouse", "datacenters", "eval", "dc_fixture.py"))
dcfx = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dcfx)

FRESH = False
TABLES = {"deals": ["energy_deals", "energy_deals_evidence"], "datacenters": ["datacenter_projects", "datacenter_projects_evidence"]}


def run(step, day, cap, keep, src_out, src_root):
    import anthropic
    ex = dfx.load_extract() if step == "deals" else dcfx.load_extract()
    key = ex.ip.load_key("ANTHROPIC_API_KEY", print)
    real = anthropic.Anthropic(api_key=key)
    model = ex.pick_model(real, print)
    rec = dfx.Recorder(real, cap, model)
    box = dfx.sandbox if step == "deals" else dcfx.sandbox
    with box(ex, rec, model) as tmp:
        for t in TABLES[step] + ["news_stories"]:
            shutil.copyfile(os.path.join(src_out, t + ".csv"), os.path.join(tmp, t + ".csv"))
        news = pd.read_csv(os.path.join(tmp, "news_stories.csv"), skiprows=_hdr(os.path.join(tmp, "news_stories.csv")), dtype=str, keep_default_na=False,
                           usecols=["event_id", "event_date"])
        todays = set(news.loc[news["event_date"].str[:10] == day, "event_id"])
        chk = pd.read_csv(os.path.join(src_root, "warehouse", step, "checked.csv"), dtype=str, keep_default_na=False)
        again = chk["story_id"].isin(todays)
        chk[~again].to_csv(ex.CHECKED, index=False, lineterminator="\n")
        if FRESH:   # --fresh: the rows whose every story is of the day are taken out, as before that day's first run
            p = os.path.join(tmp, TABLES[step][0] + ".csv")
            with open(p, encoding="utf-8") as f:
                head = [x for x in f if x.startswith("#")]
            t0 = pd.read_csv(p, skiprows=_hdr(p), dtype=str, keep_default_na=False)
            only = t0["story_ids"].apply(lambda s: set(s.split(";")) <= todays)
            t0[~only].to_csv(p + ".body", index=False, lineterminator="\n")
            with open(p, "w", encoding="utf-8", newline="") as f:
                f.writelines(head)
                f.write(open(p + ".body", encoding="utf-8").read())
            os.remove(p + ".body")
            print(f"{step}: --fresh: {int(only.sum())} rows of {day} taken out")
        before = {t: pd.read_csv(os.path.join(tmp, t + ".csv"), skiprows=_hdr(os.path.join(tmp, t + ".csv")), dtype=str, keep_default_na=False)
                  for t in TABLES[step]}
        rc = ex.main(["--max-calls", "20"])
        log = dfx.log_of(tmp)
        after = {t: pd.read_csv(os.path.join(tmp, t + ".csv"), skiprows=_hdr(os.path.join(tmp, t + ".csv")), dtype=str, keep_default_na=False)
                 for t in TABLES[step]}
        os.makedirs(keep, exist_ok=True)
        main_t = TABLES[step][0]
        key_col = "event_id" if step == "deals" else "entity_id"
        new = after[main_t][~after[main_t][key_col].isin(set(before[main_t][key_col]))]
        touched = after[main_t][after[main_t]["story_ids"].apply(lambda s: bool(set(s.split(";")) & todays))]
        new.to_csv(os.path.join(keep, f"{step}_new_rows.csv"), index=False)
        touched.to_csv(os.path.join(keep, f"{step}_rows_of_the_day.csv"), index=False)
        with open(os.path.join(keep, f"{step}_log.txt"), "w", encoding="utf-8") as f:
            f.write(log)
    print(f"{step}: exit {rc}; {int(again.sum())} stories of {day} sent again; rows before {len(before[main_t])}, "
          f"after {len(after[main_t])}, new {len(new)}, rows holding the day's stories {len(touched)}; "
          f"{len(rec.calls)} calls, USD {rec.spent:.4f}")
    for c in rec.calls:
        print(f"  call: {c['tokens']} USD {c['usd']:.4f} {c['stop_reason']} {c['request_id']}")
    return rec.spent


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--day", required=True)
    ap.add_argument("--cap", type=float, default=1.0)
    ap.add_argument("--keep", required=True)
    ap.add_argument("--src", default=os.path.join(ROOT, "warehouse", "output"))
    ap.add_argument("--fresh", action="store_true", help="take out the rows whose every story is of the day first")
    args = ap.parse_args(argv)
    global FRESH
    FRESH = args.fresh
    spent = 0.0
    for step in ("deals", "datacenters"):
        spent += run(step, args.day, args.cap - spent, os.path.join(args.keep), args.src, ROOT)
    print(f"total USD {spent:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
