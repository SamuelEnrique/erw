"""Energy Research Warehouse (ERW), session 7508 (chain 304): the rows of eia930_demand_growth computed again from
EIA's hourly demand, by the rule of docs/methods/demand_growth.md and docs/methods/eia930_demand_growth.md, and set
beside the table. Written from the two notes; it imports nothing of the builder.

    python replication/demand_growth/extract_hours.py <folder of EIA's workbooks> <hours folder>
    python replication/demand_growth/from_hourly.py <hours folder> <eia930_demand_growth.csv> [--api=<eia930_all_demand.csv>] [--out=<from_hourly.json>]

The rule, as the notes give it (section "The rule in full" of demand_growth.md, completed by this session):

1. An hour is dated by its start: EIA's "UTC time" is the hour's end, and one hour is taken off.
2. California (CISO): an hour whose start is from 2023-10-31T23:00Z to 2025-12-02T22:00Z is read one hour earlier.
   The hour EIA wrote at 2023-10-31T22:00Z stays and the one moved onto it is dropped; 2025-12-02T22:00Z is left empty.
3. An hour is used when it is held, above zero, within 25 percent of the median of those of the two hours before and
   the two hours after that are held and above zero, and from a third of to three times the area's median hour.
4. Years, months and hours of the day are the area's local time. A whole year is written when at least 95 percent of
   its hours are used; a month at 95 percent; a month's hour of the day at 90 percent. Nothing is filled.
5. The year to date is 1 January to the end of the month the table's header names, of every year.
6. Growth is of the means and peaks as the table writes them (MW to one decimal): percent to two decimals, MW to one.

The workbooks on this machine are EIA's of 3 October 2026; the table was built on 6 November from EIA's of 5 November.
So (a) a value EIA revised between the two differs, and is listed, and (b) the hours of 4 to 31 October 2026 are not
in these workbooks: with --api they are read from EIA's hourly route as the warehouse holds it (eia930_all_demand,
EIA's "Demand", not its adjusted column), and the two rows that need them (the year so far of 2026 and October 2026)
are reported apart, as from a second source. Without --api those rows are not recomputed, and the count says so.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

AREAS = {"ERCO": "America/Chicago", "MISO": "America/Chicago", "SWPP": "America/Chicago", "CISO": "America/Los_Angeles",
         "PJM": "America/New_York", "NYIS": "America/New_York", "ISNE": "America/New_York", "US48": "America/New_York"}
BASE = 2019
JUMP = 0.25
LATE_FROM, LATE_TO = pd.Timestamp("2023-10-31T23:00:00Z"), pd.Timestamp("2025-12-02T22:00:00Z")


def table_rows(path):
    header = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#"):
                header.append(line[1:].strip())
            else:
                break
    t = pd.read_csv(path, comment="#", dtype={"x_at": "string"})
    return header, t


def hours_of(folder, area, api):
    h = pd.read_csv(os.path.join(folder, f"{area}.csv"), comment="#")
    s = pd.Series(pd.to_numeric(h["demand_mw"], errors="coerce").values,
                  index=pd.to_datetime(h["utc_end"], utc=True) - pd.Timedelta(hours=1))   # rule 1
    s = s[~s.index.duplicated(keep="last")].sort_index()
    last_held = s.dropna().index.max()
    spliced = 0
    if api is not None:
        a = api[(api["entity"] == f"eia930:{area}") & (api["variable"] == "demand_mw")]
        extra = pd.Series(a["value"].astype(float).values, index=pd.to_datetime(a["ts_utc"], utc=True)).sort_index()
        extra = extra[extra.index > last_held]
        spliced = len(extra)
        s = pd.concat([s[s.index <= last_held], extra])
    if area == "CISO":                                                                      # rule 2
        late = (s.index >= LATE_FROM) & (s.index <= LATE_TO)
        moved = s[late].copy()
        moved.index = moved.index - pd.Timedelta(hours=1)
        kept = s[~late]
        s = pd.concat([kept, moved[~moved.index.isin(kept.index)]]).sort_index()
    s = s.reindex(pd.date_range(s.index.min(), s.index.max(), freq="h", tz="UTC"))
    return s, last_held, spliced


def screen(s):
    """Rule 3. Returns the used hours and the counts of hours left out, from 2019 on."""
    ok = s.notna() & (s > 0)
    v = s.where(ok)
    around = pd.concat([v.shift(k) for k in (2, 1, -1, -2)], axis=1)
    med = around.median(axis=1, skipna=True)
    apart = ok & med.notna() & ((v - med).abs() > JUMP * med)
    centre = v.median()
    out_of_range = ok & ~apart & ((v < centre / 3) | (v > centre * 3))
    used = v.where(~apart & ~out_of_range)
    return used, {"blank": s.isna(), "not_positive": s.notna() & ~(s > 0), "apart": apart, "out_of_range": out_of_range}


def compute(area, s, ytd_month, ytd_year, with_peak, last_held):
    used_utc, left = screen(s)
    tz = AREAS[area]
    local = used_utc.index.tz_convert(tz)
    f = pd.DataFrame({"v": used_utc.values, "y": local.year, "m": local.month, "h": local.hour}, index=used_utc.index)
    f = f[f["y"] >= BASE]
    counts = {k: int(x[(x.index.tz_convert(tz).year >= BASE) & (x.index <= last_held)].sum()) for k, x in left.items()}
    out = {}      # (variable, year) -> value
    at = {}       # (variable, year) -> the peak's hour
    r1 = lambda x: round(float(x) + 0.0, 1)
    whole = []
    for y, g in f.groupby("y"):
        start, end = pd.Timestamp(year=y, month=1, day=1, tz=tz), pd.Timestamp(year=y + 1, month=1, day=1, tz=tz)
        in_year = int((end - start) / pd.Timedelta(hours=1))
        complete = f.index.max() >= end.tz_convert("UTC") - pd.Timedelta(hours=1)
        u = g["v"].dropna()
        if complete and len(u) >= 0.95 * in_year:
            whole.append(y)
            out[("avg_demand_mw", y)] = r1(u.mean())
            out[("hours_used", y)] = float(len(u))
            out[("hours_in_year", y)] = float(in_year)
            if with_peak:
                out[("peak_demand_mw", y)] = r1(u.max())
                at[("peak_demand_mw", y)] = u.idxmax()
            for hh, gh in g.groupby("h"):
                out[(f"avg_demand_mw_h{hh:02d}", y)] = r1(gh["v"].dropna().mean())
            for (mm, hh), gc in g.groupby(["m", "h"]):
                uc = gc["v"].dropna()
                if len(uc) >= 0.90 * len(gc):
                    out[(f"avg_demand_mw_m{mm:02d}_h{hh:02d}", y)] = r1(uc.mean())
        # the year to date: 1 January to the end of the header's month, of every year
        if y < ytd_year or (y == ytd_year):
            w_end = pd.Timestamp(year=y + (ytd_month == 12), month=ytd_month % 12 + 1, day=1, tz=tz)
            in_window = int((w_end - start) / pd.Timedelta(hours=1))
            gw = g[g.index < w_end.tz_convert("UTC")]
            uw = gw["v"].dropna()
            have_all = f.index.max() >= w_end.tz_convert("UTC") - pd.Timedelta(hours=1)
            if have_all and len(uw) >= 0.95 * in_window:
                out[("ytd_avg_demand_mw", y)] = r1(uw.mean())
                out[("ytd_hours_used", y)] = float(len(uw))
                out[("ytd_hours_in_window", y)] = float(in_window)
                if with_peak:
                    out[("ytd_peak_demand_mw", y)] = r1(uw.max())
                    at[("ytd_peak_demand_mw", y)] = uw.idxmax()
        for mm, gm in g.groupby("m"):
            m_start = pd.Timestamp(year=y, month=mm, day=1, tz=tz)
            m_end = pd.Timestamp(year=y + (mm == 12), month=mm % 12 + 1, day=1, tz=tz)
            in_month = int((m_end - m_start) / pd.Timedelta(hours=1))
            um = gm["v"].dropna()
            if f.index.max() >= m_end.tz_convert("UTC") - pd.Timedelta(hours=1) and len(um) >= 0.95 * in_month:
                out[(f"avg_demand_mw_m{mm:02d}", y)] = r1(um.mean())
    pct = lambda a, b: round((a / b - 1) * 100 + 0.0, 2)
    for y in whole:                                                                        # rule 6
        if y > BASE:
            out[("avg_demand_growth_since_2019_pct", y)] = pct(out[("avg_demand_mw", y)], out[("avg_demand_mw", BASE)])
            if (("avg_demand_mw", y - 1)) in out:
                out[("avg_demand_growth_yoy_pct", y)] = pct(out[("avg_demand_mw", y)], out[("avg_demand_mw", y - 1)])
            if with_peak:
                out[("peak_demand_growth_since_2019_pct", y)] = pct(out[("peak_demand_mw", y)], out[("peak_demand_mw", BASE)])
    for (var, y) in [k for k in out if k[0] == "ytd_avg_demand_mw" and k[1] > BASE]:
        out[("ytd_avg_demand_growth_since_2019_pct", y)] = pct(out[(var, y)], out[(var, BASE)])
        if with_peak:
            out[("ytd_peak_demand_growth_since_2019_pct", y)] = pct(out[("ytd_peak_demand_mw", y)], out[("ytd_peak_demand_mw", BASE)])
    last = max(whole) if whole else None
    if last and last > BASE:
        for (var, y) in [k for k in out if k[1] == last and k[0].startswith("avg_demand_mw_")]:
            if (var, BASE) in out:
                tail = var[len("avg_demand_mw_"):]
                out[(f"growth_mw_{tail}", last)] = round(out[(var, last)] - out[(var, BASE)] + 0.0, 1)
                out[(f"growth_pct_{tail}", last)] = pct(out[(var, last)], out[(var, BASE)])
    return out, at, counts


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opt = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--") and "=" in a)
    if len(args) != 2:
        raise SystemExit(__doc__)
    folder, table_file = args
    header, t = table_rows(table_file)
    import re
    m = re.search(r"year to date: 1 January to the end of (\d{2})/(\d{4})", "\n".join(header))
    ytd_month, ytd_year = int(m.group(1)), int(m.group(2))
    api = None
    if "api" in opt:
        api = pd.read_csv(opt["api"], comment="#", usecols=["entity", "variable", "ts_utc", "value"])
    t["year"] = t["ts_utc"].str[:4].astype(int)
    report = {"table_file": os.path.basename(table_file), "table_rows": int(len(t)), "ytd_through": f"{ytd_month:02d}/{ytd_year}",
              "areas": {}, "differences": [], "second_source": []}
    n_equal = n_cmp = n_not = n_second = n_second_equal = n_extra = 0
    for area in AREAS:
        s, last_held, spliced = hours_of(folder, area, api)
        out, at, counts = compute(area, s, ytd_month, ytd_year, with_peak=(area != "US48"), last_held=last_held)
        rows = t[t["entity"] == f"eia930:{area}"]
        held = {(r.variable, r.year): (float(r.value), r.x_at if isinstance(r.x_at, str) else None) for r in rows.itertuples()}
        # the rows that need an hour after the workbook's last: the newest year's year to date and its last month
        needs_api = {k for k in held if k[1] == ytd_year and (k[0].startswith("ytd_") or k[0] == f"avg_demand_mw_m{ytd_month:02d}")}
        a_eq = a_cmp = 0
        for k, (value, x_at) in sorted(held.items()):
            second = k in needs_api
            if k not in out:
                n_not += 1
                report["differences"].append({"area": area, "variable": k[0], "year": k[1], "table": value, "recomputed": None,
                                              "why": "needs hours after the workbook's last" if second else "not written by the rule"})
                continue
            same = abs(out[k] - value) < 1e-9
            if same and k in at and x_at:
                same = at[k].strftime("%Y-%m-%dT%H:%M:%SZ") == x_at
            if second:
                n_second += 1
                n_second_equal += same
                report["second_source"].append({"area": area, "variable": k[0], "year": k[1], "table": value, "recomputed": out[k]})
                continue
            n_cmp += 1
            a_cmp += 1
            n_equal += same
            a_eq += same
            if not same:
                report["differences"].append({"area": area, "variable": k[0], "year": k[1], "table": value, "recomputed": out[k],
                                              "x_at_table": x_at, "x_at_recomputed": at[k].strftime("%Y-%m-%dT%H:%M:%SZ") if k in at else None})
        extra = sorted(k for k in out if k not in held)
        n_extra += len(extra)
        for k in extra:
            report["differences"].append({"area": area, "variable": k[0], "year": k[1], "table": None, "recomputed": out[k], "why": "the rule writes it, the table does not hold it"})
        report["areas"][area] = {"last_hour_held_in_workbook": last_held.strftime("%Y-%m-%dT%H:%M:%SZ"), "hours_from_api": spliced,
                                 "left_out_since_2019": counts, "rows_in_table": len(held), "compared": a_cmp, "equal": a_eq}
        print(f"{area}: {a_eq} of {a_cmp} rows equal; left out since 2019: {counts}; workbook to {last_held:%Y-%m-%d %H:%M}Z, {spliced} hours from the hourly route", flush=True)
    report["summary"] = {"compared": n_cmp, "equal": n_equal, "second_source_rows": n_second, "second_source_equal": int(n_second_equal),
                         "not_recomputed": n_not, "recomputed_not_in_table": n_extra}
    print(f"From EIA's hourly demand (workbooks of 3 October 2026): {n_equal} of {n_cmp} rows of {len(t)} equal the table's; "
          f"{n_second} rows need hours after the workbooks' last ({n_second_equal} equal from EIA's hourly route); "
          f"{n_not} not recomputed; {n_extra} recomputed and not in the table")
    if "out" in opt:
        with open(opt["out"], "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
