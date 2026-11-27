#!/usr/bin/env python3
"""ERW, energy equities (/equities): an independent replication of the page files' company figures (session 10000, chain
701, part D's done line).

Written from docs/methods/equities.md ("The universe", "The statements") and the two tables alone, not from
warehouse/derived/equity_page_files.py. It reads equity_universe and equity_fundamentals_quarterly (warehouse/output, or
--tables DIR; on Redivis the same tables) and the page's files (site/data/equities/index.json and series/<ticker>.json),
and checks:

  the segments    each company's segments are its SEC industry code's under the method note's table (a code that names
                  two segments in both), and each segment's n_companies is the count of companies in it
  the companies   index.json lists every universe company once, with its CIK, ticker, exchange and SIC
  the statements  each company's quarterly rows are, for each filing in the table, the filing's own period (the newest
                  period end among that filing's rows), one row a period length; revenue, net income and capex the
                  duration rows of that length, debt and shares outstanding the instants at that end; filed the vintage
  the prices      every close, adjusted close, volume and market value is null with a reason (no source a license allows)

Prints N of N and each difference. Exit 0 when all agree, 1 when one does not, 2 when the inputs cannot be read.
Standard library only.

    python replication/equities/replicate.py [--tables DIR] [--site DIR]
"""
import argparse
import csv
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
csv.field_size_limit(10 ** 9)

# docs/methods/equities.md, "The universe": the SEC industry codes of each segment
CODES = {
    "exploration_production": {"1311"},
    "integrated_oil_gas": {"2911"}, "refining": {"2911"},
    "oilfield_services": {"1381", "1382", "1389", "3533"},
    "midstream_pipelines": {"4610", "4922", "4923", "4924"},
    "regulated_utilities": {"4931", "4932", "4939", "4911", "4923", "4924"},
    "independent_power": {"4991", "4911"},
    "coal": {"1220", "1221", "1222"},
    "grid_equipment": {"3612", "3613"},
}
NONE = ["lng", "nuclear_uranium", "solar", "wind", "storage", "hydrogen_fuel_cells"]
LINES = {"revenue": "revenue", "net_income": "net_income", "capex": "capex", "long_term_debt_usd": "debt",
         "shares_outstanding": "shares_outstanding"}


def read_table(path):
    with open(path, encoding="utf-8", newline="") as f:
        lines = (ln for ln in f if not ln.startswith("#"))
        return list(csv.DictReader(lines))


def num(v):
    if v in ("", None):
        return None
    x = float(v)
    return int(x) if x.is_integer() else x


def expected_quarterly(rows):
    own = {}
    for r in rows:
        own[r["x_accession"]] = max(own.get(r["x_accession"], ""), r["ts_utc"])
    groups = defaultdict(lambda: {"inst": {}, "dur": defaultdict(dict), "base": None})
    for r in rows:
        if r["ts_utc"] != own[r["x_accession"]]:
            continue
        g = groups[(r["x_accession"], r["ts_utc"])]
        g["base"] = g["base"] or r
        v = r["variable"]
        if r["x_months"] == "":
            if v in LINES:
                g["inst"][LINES[v]] = num(r["value"])
        else:
            line = v.rsplit("_", 2)[0]   # revenue_3m_usd -> revenue
            if line in LINES:
                g["dur"][(r["x_months"], r["x_period_start"])][LINES[line]] = num(r["value"])
    out = []
    for (acc, end), g in groups.items():
        b = g["base"]
        durs = list(g["dur"].items()) or [((None, None), {})]
        for (m, start), vals in durs:
            out.append({"period_start": start, "period_end": end[:10], "months": num(m) if m else None, "filed": b["vintage"][:10],
                        "form": b["x_form"], "accession": acc, "revenue": vals.get("revenue"), "net_income": vals.get("net_income"),
                        "capex": vals.get("capex"), "debt": g["inst"].get("debt"),
                        "shares_outstanding": g["inst"].get("shares_outstanding")})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables", default=os.path.join(ROOT, "warehouse", "output"))
    ap.add_argument("--site", default=os.path.join(ROOT, "site", "data", "equities"))
    a = ap.parse_args(argv)
    try:
        uni = read_table(os.path.join(a.tables, "equity_universe.csv"))
        fund = read_table(os.path.join(a.tables, "equity_fundamentals_quarterly.csv"))
        index = json.load(open(os.path.join(a.site, "index.json"), encoding="utf-8"))
    except OSError as e:
        print(f"cannot read the inputs: {e}")
        return 2
    checks, bad = 0, []

    def check(ok, what):
        nonlocal checks
        checks += 1
        if not ok:
            bad.append(what)

    listed = {c["cik"]: c for c in index["companies"]}
    check(len(listed) == len(uni) == len(index["companies"]), f"companies: index {len(index['companies'])}, table {len(uni)}")
    count = defaultdict(int)
    for u in uni:
        segs = sorted(s for s, codes in CODES.items() if u["sic"] in codes)
        for s in segs:
            count[s] += 1
        check(sorted(u["segments"].split(";")) == segs, f"{u['ticker']}: segments {u['segments']} against {segs}")
        c = listed.get(u["cik"])
        check(c is not None, f"{u['ticker']}: not in index.json")
        if c:
            check((c["ticker"], c["exchange"], c["sic"], sorted(c["segments"])) == (u["ticker"], u["exchange"], u["sic"], segs),
                  f"{u['ticker']}: index fields")
    for s in index["segments"]:
        want = 0 if s["id"] in NONE else count[s["id"]]
        check(s["n_companies"] == want, f"segment {s['id']}: n_companies {s['n_companies']} against {want}")
    by_entity = defaultdict(list)
    for r in fund:
        by_entity[r["entity"]].append(r)
    for u in uni:
        f = json.load(open(os.path.join(a.site, "series", u["ticker"].upper() + ".json"), encoding="utf-8"))
        cols = f["quarterly_columns"]
        got = sorted((dict(zip(cols, r)) for r in f["quarterly"]), key=lambda r: (r["accession"], r["months"] or 0, r["period_start"] or ""))
        want = sorted(expected_quarterly(by_entity.get(u["entity_id"], [])), key=lambda r: (r["accession"], r["months"] or 0, r["period_start"] or ""))
        check(len(got) == len(want), f"{u['ticker']}: {len(got)} quarterly rows against {len(want)}")
        for g, w in zip(got, want):
            same = all(g[k] == w[k] for k in w)
            check(same, f"{u['ticker']} {w['accession']} {w['months']}: {[(k, g[k], w[k]) for k in w if g[k] != w[k]][:3]}")
        check(f["daily"] == [] and all(f["held"].get(k) for k in ("close", "adj_close", "volume", "market_value")),
              f"{u['ticker']}: a price shown or a column held without its reason")
    print(f"{checks - len(bad)} of {checks} checks agree")
    for b in bad[:30]:
        print("  DIFFERS:", b)
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
