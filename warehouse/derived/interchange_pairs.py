#!/usr/bin/env python3
"""Who trades with whom: every pair of balancing authorities and every pair of regions, each side's report, their mean,
their gap and the direction, by day and by month; each authority's partners by year; and each pair across the nine
events of /events beside the same calendar hours of the other years (session 8002, chain 501 part C).

Energy Research Warehouse (ERW). Four derived tables and one page file. Descriptive only: sums, means of the two
reports, counts and ranks; no model, no estimate. Method: docs/methods/interchange_pairs.md. The page file's shape:
docs/state/page_files_regions.md, section 7.

    python warehouse/derived/interchange_pairs.py                 # the four tables (data lock) and site/data/regions/trade_matrix.json
    python warehouse/derived/interchange_pairs.py --out-dir DIR   # a trial: the tables and the page file under DIR

    interchange_pair_daily     entity eia930:<A>-<B> (A before B by code), variable interchange_mwh, freq P1D, ts_utc the
                               Eastern day at 00:00:00Z
    interchange_pair_monthly   the same by Eastern month, freq P1M
    ba_trade_partners          freq P1Y: exchange_gross_mwh and net_import_mwh, entity eia930:<BA>-<partner> (x_ba, x_partner,
                               x_rank_gross, x_rank_net), and net_import_share_of_demand_pct, entity eia930:<BA>
    interchange_event_pairs    entity eia930:<A>-<B>, variable interchange_mwh, one row an event and a year (x_event,
                               x_year, x_role event or other_year), freq PT1H summed over the window (ts_utc its start)

Inputs: eia930_ba_interchange_hourly_<2018 to 2026> (each authority's own report its own row, positive when it sends
power to the neighbour), eia930_region_pair_hourly (each region pair, both sides), eia930_ba_supply_hourly (each
authority's total interchange) and eia930_ba_demand_hourly (its demand).

THE PAIR RULE (both levels). For a pair A-B, A's report is read as power from A to B as A filed it; B's report of the same
tie is turned to the same direction. Over a day or a month: x_a_report_mwh is the sum of A's reported hours, x_b_report_mwh
of B's; x_hours_a, x_hours_b and x_hours_both count them; over the hours both reported, x_gap_mwh is A's less B's, and
value is the mean of the two (x_basis mean). Where no hour has both, value is the one side that reported (x_basis a or b).
x_direction is a_to_b when value is above zero, b_to_a below, none at zero. For region pairs the two sides are the region
pair table's first and second reports (eia930_region_pair_hourly, docs/methods/eia930_region_hourly.md).
"""

import argparse
import datetime as dt
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

SOURCE = "erw:interchange_pairs"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/interchange_pairs.md"
YEARS = range(2018, 2027)
ET = "America/New_York"
PAIR_COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "source", "x_level", "x_a", "x_b", "x_basis",
             "x_a_report_mwh", "x_b_report_mwh", "x_gap_mwh", "x_hours_a", "x_hours_b", "x_hours_both", "x_direction"]
PARTNER_COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "source", "x_ba", "x_partner", "x_rank_gross", "x_rank_net", "x_hours"]
EVENT_COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "source", "x_level", "x_a", "x_b", "x_event", "x_year",
              "x_role", "x_window_end", "x_basis", "x_a_report_mwh", "x_b_report_mwh", "x_gap_mwh", "x_hours_a", "x_hours_b",
              "x_hours_both", "x_direction"]
ACC = ["a_sum", "a_n", "b_sum", "b_n", "mean_both", "gap_both", "n_both"]


def read(name, cols):
    p = os.path.join(ip.OUT_DIR if os.path.exists(os.path.join(ip.OUT_DIR, name + ".csv")) else os.path.join(ROOT, "warehouse", "output"), name + ".csv")
    fh = open(p, "rb")
    for _ in range(ip.header_rows(p)):
        fh.readline()
    d = pd.read_csv(fh, usecols=cols, engine="pyarrow")
    fh.close()
    d["ts"] = pd.to_datetime(d["ts_utc"], utc=True)
    return d


def hourly_pairs_ba(year):
    """One row a pair-hour: a (A's report, A to B) and b (B's report turned to A to B), A before B by code."""
    d = read(f"eia930_ba_interchange_hourly_{year}", ["entity", "ts_utc", "value"])
    ent = d["entity"].str.slice(len("eia930:"))
    parts = ent.str.split("-", n=1, expand=True)
    d["rep"], d["nb"] = parts[0], parts[1]
    first = d["rep"] < d["nb"]
    d["A"] = np.where(first, d["rep"], d["nb"])
    d["B"] = np.where(first, d["nb"], d["rep"])
    d["side"] = np.where(first, "a", "b")
    d["v"] = np.where(first, d["value"], -d["value"])
    w = d.pivot_table(index=["A", "B", "ts"], columns="side", values="v", aggfunc="sum").reset_index()
    for c in ("a", "b"):
        if c not in w:
            w[c] = np.nan
    w["level"] = "ba"
    return w[["level", "A", "B", "ts", "a", "b"]]


def hourly_pairs_region():
    d = read("eia930_region_pair_hourly", ["entity", "ts_utc", "x_first_report", "x_second_report"])
    parts = d["entity"].str.slice(len("eia930:")).str.split("-", n=1, expand=True)
    return pd.DataFrame({"level": "region", "A": parts[0], "B": parts[1], "ts": d["ts"], "a": d["x_first_report"], "b": d["x_second_report"]})


def accumulate(w, key):
    both = w["a"].notna() & w["b"].notna()
    t = pd.DataFrame({"level": w["level"], "A": w["A"], "B": w["B"], "k": key,
                      "a_sum": w["a"].fillna(0.0), "a_n": w["a"].notna().astype(int),
                      "b_sum": w["b"].fillna(0.0), "b_n": w["b"].notna().astype(int),
                      "mean_both": ((w["a"] + w["b"]) / 2).where(both, 0.0), "gap_both": (w["a"] - w["b"]).where(both, 0.0),
                      "n_both": both.astype(int)})
    return t.groupby(["level", "A", "B", "k"], as_index=False)[ACC].sum()


def pair_rows(acc, freq, ts_of):
    a = acc.groupby(["level", "A", "B", "k"], as_index=False)[ACC].sum()
    value = np.where(a["n_both"] > 0, a["mean_both"], np.where(a["a_n"] > 0, a["a_sum"], a["b_sum"]))
    basis = np.where(a["n_both"] > 0, "mean", np.where(a["a_n"] > 0, "a", "b"))
    out = pd.DataFrame({"entity": "eia930:" + a["A"] + "-" + a["B"], "variable": "interchange_mwh", "ts_utc": a["k"].map(ts_of),
                        "value": np.round(value, 1), "unit": "MWh", "freq": freq, "source": SOURCE, "x_level": a["level"],
                        "x_a": a["A"], "x_b": a["B"], "x_basis": basis,
                        "x_a_report_mwh": np.where(a["a_n"] > 0, np.round(a["a_sum"], 1), np.nan),
                        "x_b_report_mwh": np.where(a["b_n"] > 0, np.round(a["b_sum"], 1), np.nan),
                        "x_gap_mwh": np.where(a["n_both"] > 0, np.round(a["gap_both"], 1), np.nan),
                        "x_hours_a": a["a_n"], "x_hours_b": a["b_n"], "x_hours_both": a["n_both"],
                        "x_direction": np.where(value > 0, "a_to_b", np.where(value < 0, "b_to_a", "none"))})
    return out.sort_values(["entity", "ts_utc"]).reset_index(drop=True)


def event_windows():
    import event_window as ew
    evs = [dict(event=ew.EVENTS[0]["event"], start=ew.EVENTS[0]["start"], end=ew.EVENTS[0]["end"])]
    evs += [dict(event=e["event"], start=e["start"], end=e["end"]) for e in ew.MULTI]
    out = []
    for e in evs:
        y0 = int(e["start"][:4])
        for y in YEARS:
            k = y - y0
            try:
                s = (pd.Timestamp(e["start"]) + pd.DateOffset(years=k)).strftime("%Y-%m-%d")
                en = (pd.Timestamp(e["end"]) + pd.DateOffset(years=k)).strftime("%Y-%m-%d")
            except ValueError:
                continue
            start = pd.Timestamp(s, tz=ET).tz_convert("UTC")
            end = (pd.Timestamp(en, tz="America/Los_Angeles") + pd.Timedelta(days=1)).tz_convert("UTC")
            out.append(dict(event=e["event"], year=y, role="event" if k == 0 else "other_year", start=start, end=end))
    return out


def fmt_csv(df, path, header, log):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        for h in header:
            f.write("# " + h + "\n")
        df.to_csv(f, index=False, lineterminator="\n", float_format="%.10g")
    os.replace(tmp, path)
    log(f"  {os.path.basename(path)}: {len(df):,} rows")
    print(f"{os.path.basename(path)}: rows={len(df):,}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Who trades with whom (chain 501 part C)")
    ap.add_argument("--out-dir")
    a = ap.parse_args(argv)
    src_out = os.path.join(ROOT, "warehouse", "output")
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    log_dir = os.path.join(a.out_dir, "logs") if a.out_dir else ip.LOG_DIR
    os.makedirs(log_dir, exist_ok=True)
    log = ip.Log(os.path.join(log_dir, f"interchange_pairs_{run_id}.log"))
    names = ["interchange_pair_daily", "interchange_pair_monthly", "ba_trade_partners", "interchange_event_pairs"]
    for n in names:
        ip._require_lock(os.path.join(ip.OUT_DIR, n + ".csv"), f"writing {n}")
    windows = event_windows()
    daily, monthly, events, partners = [], [], [], []
    sources = []
    for y in list(YEARS) + ["region"]:
        if y == "region":
            w = hourly_pairs_region()
            tag = "eia930_region_pair_hourly"
        else:
            p = os.path.join(src_out, f"eia930_ba_interchange_hourly_{y}.csv")
            if not os.path.exists(p):
                raise FileNotFoundError(p)
            w = hourly_pairs_ba(y)
            tag = f"eia930_ba_interchange_hourly_{y}"
        sources.append(tag)
        et = w["ts"].dt.tz_convert(ET)
        day = et.dt.strftime("%Y-%m-%d")
        month = et.dt.strftime("%Y-%m")
        daily.append(accumulate(w, day))
        monthly.append(accumulate(w, month))
        for win in windows:
            m = (w["ts"] >= win["start"]) & (w["ts"] < win["end"])
            if m.any():
                k = f"{win['event']}|{win['year']}|{win['role']}|{ip.utc_iso(win['start'])}|{ip.utc_iso(win['end'])}"
                events.append(accumulate(w[m], pd.Series(k, index=w.index[m])))
        if y != "region":
            # each authority's own report with each partner, by Eastern year: gross (absolute) and net imports
            g = w.copy()
            g["year"] = et.dt.year
            for me, col, sign in (("A", "a", -1.0), ("B", "b", 1.0)):   # A's imports are -a; B's imports are +b
                x = g[g[col].notna()]
                partners.append(pd.DataFrame({"ba": x[me], "partner": x["B" if me == "A" else "A"], "year": x["year"],
                                              "gross": x[col].abs(), "net": sign * x[col], "n": 1})
                                .groupby(["ba", "partner", "year"], as_index=False)[["gross", "net", "n"]].sum())
        log(f"  {tag}: {len(w):,} pair-hours")
        print(f"  {tag}: {len(w):,} pair-hours", flush=True)
        del w
    d_rows = pair_rows(pd.concat(daily, ignore_index=True), "P1D", lambda k: f"{k}T00:00:00Z")
    m_rows = pair_rows(pd.concat(monthly, ignore_index=True), "P1M", lambda k: f"{k}-01T00:00:00Z")
    ev = pd.concat(events, ignore_index=True)
    e_rows = pair_rows(ev, "PT1H", lambda k: k)
    kk = e_rows["ts_utc"].str.split("|", expand=True)
    e_rows["x_event"], e_rows["x_year"], e_rows["x_role"], e_rows["ts_utc"], e_rows["x_window_end"] = kk[0], kk[1].astype(int), kk[2], kk[3], kk[4]
    e_rows = e_rows[EVENT_COLS].sort_values(["x_event", "entity", "x_year"]).reset_index(drop=True)
    # partners
    pt = pd.concat(partners, ignore_index=True).groupby(["ba", "partner", "year"], as_index=False)[["gross", "net", "n"]].sum()
    pt["rank_gross"] = pt.groupby(["ba", "year"])["gross"].rank(ascending=False, method="min").astype(int)
    pt["rank_net"] = pt.groupby(["ba", "year"])["net"].transform(lambda s: s.abs().rank(ascending=False, method="min")).astype(int)
    rows = []
    for r in pt.itertuples():
        base = dict(entity=f"eia930:{r.ba}-{r.partner}", x_ba=r.ba, ts_utc=f"{int(r.year)}-01-01T00:00:00Z", unit="MWh", freq="P1Y", source=SOURCE,
                    x_partner=r.partner, x_rank_gross=r.rank_gross, x_rank_net=r.rank_net, x_hours=int(r.n))
        rows.append({**base, "variable": "exchange_gross_mwh", "value": round(float(r.gross), 1)})
        rows.append({**base, "variable": "net_import_mwh", "value": round(float(r.net), 1)})
    # each authority's share of demand met by net imports: its own total interchange (sign turned) over its demand, the
    # hours both are held, by Eastern year
    sup = read("eia930_ba_supply_hourly", ["entity", "variable", "ts_utc", "value"])
    ti = sup[sup["variable"] == "total_interchange_mw"][["entity", "ts", "value"]].rename(columns={"value": "ti"})
    del sup
    dem = read("eia930_ba_demand_hourly", ["entity", "variable", "ts_utc", "value"])
    dm = dem[dem["variable"] == "demand_mw"][["entity", "ts", "value"]].rename(columns={"value": "dem"})
    del dem
    j = ti.merge(dm, on=["entity", "ts"], how="inner")
    j["year"] = j["ts"].dt.tz_convert(ET).dt.year
    sh = j.groupby(["entity", "year"]).agg(ni=("ti", lambda s: -s.sum()), dem=("dem", "sum"), n=("ti", "size")).reset_index()
    for r in sh.itertuples():
        if r.dem > 0:
            rows.append(dict(entity=r.entity, variable="net_import_share_of_demand_pct", ts_utc=f"{int(r.year)}-01-01T00:00:00Z",
                             value=round(100 * float(r.ni) / float(r.dem), 3), unit="pct", freq="P1Y", source=SOURCE,
                             x_ba=r.entity.split(":")[1], x_partner="", x_rank_gross="", x_rank_net="", x_hours=int(r.n)))
    p_rows = pd.DataFrame(rows)[PARTNER_COLS].sort_values(["entity", "ts_utc", "variable", "x_partner"]).reset_index(drop=True)
    common = [
        f"Retrieved: {run_id} (UTC) by warehouse/derived/interchange_pairs.py",
        f"Run log: warehouse/output/logs/interchange_pairs_{run_id}.log",
        f"Source: {SOURCE} ERW derived table, {METHOD_URL}",
        "Derived from: " + "; ".join(sources) + "; eia930_ba_supply_hourly; eia930_ba_demand_hourly",
        "License: public (derived by the ERW from U.S. Energy Information Administration data, Form EIA-930).",
    ]
    rule = ("A's report is power from A to B as A filed it (A before B by code); B's report of the same tie is turned to that direction. "
            "x_a_report_mwh and x_b_report_mwh sum each side's reported hours (x_hours_a, x_hours_b); over the hours both reported "
            "(x_hours_both), x_gap_mwh is A's less B's and value is the mean of the two (x_basis mean); where no hour has both, value is "
            "the side that reported (x_basis a or b). x_direction: a_to_b above zero, b_to_a below. x_level: ba or region (region pairs "
            "from eia930_region_pair_hourly's first and second reports). Method: docs/methods/interchange_pairs.md.")
    out = {}
    out["interchange_pair_daily"] = (d_rows[PAIR_COLS], [
        "Energy Research Warehouse (ERW): interchange between every pair of balancing authorities and every pair of EIA's regions, each side's report, their mean and gap, by Eastern day, July 2018 on (session 8002, chain 501)",
        "Shape: series (docs/datastandard.md v0). entity eia930:<A>-<B>, variable interchange_mwh, MWh, freq P1D, ts_utc the Eastern day at 00:00:00Z. " + rule])
    out["interchange_pair_monthly"] = (m_rows[PAIR_COLS], [
        "Energy Research Warehouse (ERW): interchange between every pair of balancing authorities and every pair of EIA's regions, each side's report, their mean and gap, by Eastern month, July 2018 on (session 8002, chain 501)",
        "Shape: series (docs/datastandard.md v0). entity eia930:<A>-<B>, variable interchange_mwh, MWh, freq P1M, ts_utc the first day of the Eastern month at 00:00:00Z. " + rule])
    out["ba_trade_partners"] = (p_rows, [
        "Energy Research Warehouse (ERW): each balancing authority's trading partners by year, ranked by gross and by net exchange, and its share of demand met by net imports (session 8002, chain 501)",
        "Shape: series (docs/datastandard.md v0). freq P1Y, ts_utc the first day of the Eastern year. Partner rows: entity eia930:<BA>-<partner> from the authority's side (x_ba, x_partner). exchange_gross_mwh: the sum of the absolute "
        "hourly flows with x_partner by the authority's own report; net_import_mwh: the same flows signed, positive when it received power; x_rank_gross and x_rank_net "
        "rank its partners within the year (net by size, whichever direction); x_hours the hours it reported. net_import_share_of_demand_pct: its total interchange "
        "with the sign turned, summed over the hours it holds both that and its demand, over its demand in the same hours, percent (below zero: a net exporter); entity eia930:<BA>. Method: docs/methods/interchange_pairs.md."])
    out["interchange_event_pairs"] = (e_rows, [
        "Energy Research Warehouse (ERW): each pair of balancing authorities and of regions over the window of each of the nine events of /events, beside the same calendar hours of every other year held (session 8002, chain 501)",
        "Shape: series (docs/datastandard.md v0). entity eia930:<A>-<B>, variable interchange_mwh, MWh summed over the window, freq PT1H (hourly data summed), ts_utc the window's first hour, "
        "x_window_end the hour after its last. x_event, x_year, x_role (event: the event's own window; other_year: the same calendar dates in another year). The window runs from midnight of "
        "its first day in Eastern time to midnight after its last in Pacific time. " + rule])
    for n, (df, head) in out.items():
        fmt_csv(df, os.path.join(ip.OUT_DIR, n + ".csv"), head + common + [f"File holds {len(df)} rows, one build; rebuilt whole by each run."], log)
    ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                            report="Who trades with whom: interchange by pair of balancing authorities and of regions, partners, events (docs/methods/interchange_pairs.md)",
                            report_url=METHOD_URL, document_list="docs/methods/interchange_pairs.md", license="public", tables=names)])
    # the page file
    mr = m_rows.copy()
    mr["year"] = mr["ts_utc"].str.slice(0, 4).astype(int)
    yr = mr.groupby(["x_level", "x_a", "x_b", "year"]).agg(a=("x_a_report_mwh", "sum"), b=("x_b_report_mwh", "sum"),
                                                           mean=("value", "sum"), gap=("x_gap_mwh", "sum"),
                                                           ha=("x_hours_a", "sum"), hb=("x_hours_b", "sum"), hab=("x_hours_both", "sum")).reset_index()

    def pairs_of(level):
        z = yr[yr["x_level"] == level]
        return [{"a": r.x_a, "b": r.x_b, "year": int(r.year), "a_report_mwh": round(float(r.a), 1) if r.ha else None,
                 "b_report_mwh": round(float(r.b), 1) if r.hb else None, "mean_mwh": round(float(r.mean), 1),
                 "gap_mwh": round(float(r.gap), 1) if r.hab else None, "hours_a": int(r.ha), "hours_b": int(r.hb), "hours_both": int(r.hab),
                 "direction": "a_to_b" if r.mean > 0 else ("b_to_a" if r.mean < 0 else "none")} for r in z.itertuples()]
    part = {}
    for (ba, year), g in pt.groupby(["ba", "year"]):
        part.setdefault(ba, {})[str(int(year))] = {"by_gross": list(g.sort_values("rank_gross")["partner"]),
                                                   "by_net": list(g.sort_values("rank_net")["partner"])}
    for r in sh.itertuples():
        ba = r.entity.split(":")[1]
        if r.dem > 0:
            part.setdefault(ba, {}).setdefault(str(int(r.year)), {"by_gross": [], "by_net": []})["net_import_share_of_demand_pct"] = round(100 * float(r.ni) / float(r.dem), 3)
    regions = sorted(set(yr.loc[yr["x_level"] == "region", "x_a"]) | set(yr.loc[yr["x_level"] == "region", "x_b"]))
    doc = {"built": retrieved, "tables": ["interchange_pair_monthly", "ba_trade_partners"], "method": "docs/methods/interchange_pairs.md",
           "license": "public", "years": sorted(int(y) for y in yr["year"].unique()), "regions": regions,
           "region_pairs": pairs_of("region"), "ba_pairs": pairs_of("ba"), "partners": dict(sorted(part.items()))}
    site = os.path.join(a.out_dir, "site", "trade_matrix.json") if a.out_dir else os.path.join(ROOT, "site", "data", "regions", "trade_matrix.json")
    os.makedirs(os.path.dirname(site), exist_ok=True)
    with open(site, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, separators=(",", ":"), allow_nan=False)
    log(f"  page file {site}: {os.path.getsize(site):,} bytes")
    print(f"trade_matrix.json: {os.path.getsize(site):,} bytes")
    log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
