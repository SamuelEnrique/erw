#!/usr/bin/env python3
"""The findings hunt over the whole warehouse (chain 164), family "demand": session 3004.

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-06.md. Two sources, both EIA-930 and
public: the daily demand of each balancing authority (eia930_daily_demand, 2019 on; EIA sums the day's hours in its
Eastern day), and the hourly demand of the sub-regions EIA publishes (eia930_subba_demand_hourly_<year>, 2019 to 2025).
The weekly hunt already asks weather-adjusted demand growth, record days and stress-day imports of the seven grids'
balancing authorities; here the questions are the top days, winter against summer and the peakiness of the year, of
the larger authorities outside the ISOs too, and the sub-regions' peaks, means, nights and load factors.

Faults: a day under a third or over three times its year's median is dropped (the weekly hunt's rule for EIA-930 daily
demand); an hour of a sub-region at or below zero, or over three times its year's median, is dropped the same way.
Regions of MISO, SPP, NYISO and ISO-NE are never drafted (a license is needed or a ruling holds), whoever published the
rows. EIA's region totals (CAL, MIDA, TEX and the like) are not authorities and are not read; the US48 total is.

    python warehouse/analysis/findings/deep/demand.py --dry-run
    python warehouse/analysis/findings/deep/demand.py --load
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
sys.path.insert(0, HERE)
import builder  # noqa: E402
import findings_common as common  # noqa: E402
import hunt_measures as hm  # noqa: E402

FAMILY = "demand"
YEARS = range(2019, 2026)
PCT = "averaged_inverted_cdf"   # the 99th percentile as Stata's collapse (p99) computes it
TOP_DAYS = 10
SEASON_TOP = 5
BA = {"US48": ("us48", "the lower 48 states (EIA's US48 total)"), "PJM": ("pjm_ba", "PJM"), "ERCO": ("ercot_ba", "ERCOT"),
      "CISO": ("caiso_ba", "CAISO"), "SOCO": ("ba_soco", "Southern Company's balancing authority"), "TVA": ("ba_tva", "the Tennessee Valley Authority"),
      "FPL": ("ba_fpl", "Florida Power and Light"), "DUK": ("ba_duk", "Duke Energy Carolinas"), "CPLE": ("ba_cple", "Duke Energy Progress East"),
      "BPAT": ("ba_bpat", "the Bonneville Power Administration"), "FPC": ("ba_fpc", "Duke Energy Florida"), "PACE": ("ba_pace", "PacifiCorp East"),
      "PSCO": ("ba_psco", "Public Service Company of Colorado"), "AZPS": ("ba_azps", "Arizona Public Service"), "LGEE": ("ba_lgee", "LG&E and KU"),
      "NEVP": ("ba_nevp", "NV Energy (Nevada Power)"), "WACM": ("ba_wacm", "WAPA's Rocky Mountain region"), "SRP": ("ba_srp", "the Salt River Project"),
      "SC": ("ba_sc", "Santee Cooper"), "SCEG": ("ba_sceg", "Dominion Energy South Carolina"), "LDWP": ("ba_ldwp", "the Los Angeles Department of Water and Power"),
      "PSEI": ("ba_psei", "Puget Sound Energy"), "PGE": ("ba_pge", "Portland General Electric")}
PARENT = {"PJM": ("pjm", "America/New_York", 5), "ERCO": ("ercot", "America/Chicago", 6), "CISO": ("caiso", "America/Los_Angeles", 8),
          "PNM": ("pnm", "America/Denver", 7), "MISO": ("miso", "America/Chicago", 6), "SWPP": ("spp", "America/Chicago", 6),
          "NYIS": ("nyiso", "America/New_York", 5), "ISNE": ("isone", "America/New_York", 5)}
NIGHT = (0, 5)


def daily(in_dir):
    def build():
        d = hm.series("eia930_daily_demand", in_dir, variables=["demand_mwh"], entities=[f"eia930:{b}" for b in BA])
        d = d[d["value"] > 0].drop_duplicates(["entity", "ts_utc"])
        d["ba"], d["year"], d["month"] = d["entity"].str.split(":").str[1], d["ts"].dt.year, d["ts"].dt.month
        med = d.groupby(["ba", "year"])["value"].transform("median")
        return d[(d["value"] >= med / 3) & (d["value"] <= med * 3)]
    return hm._cached(("deep_daily_demand", in_dir), build)


def _per_ba(in_dir, fn):
    rows, tables = [], {}
    for ba, g in daily(in_dir).groupby("ba"):
        region, words = BA[ba]
        for y, s in g.groupby("year"):
            v = fn(s)
            rows.append(hm._row(region, words, y, None if v is None else float(v), len(s)))
        tables[region] = ["eia930_daily_demand"]
    return {"rows": rows, "tables": tables}


def top_days(in_dir=None):
    """The mean of the year's ten highest days of demand (GWh a day)."""
    return _per_ba(in_dir, lambda s: s["value"].nlargest(TOP_DAYS).mean() / 1000)


def mean_day(in_dir=None):
    """The year's mean day of demand (GWh a day)."""
    return _per_ba(in_dir, lambda s: s["value"].mean() / 1000)


def winter_vs_summer(in_dir=None):
    """The mean of the year's five highest days in January, February and December as a percent of its five highest in June to August."""
    def f(s):
        w = s.loc[s["month"].isin([1, 2, 12]), "value"].nlargest(SEASON_TOP)
        m = s.loc[s["month"].isin([6, 7, 8]), "value"].nlargest(SEASON_TOP)
        return 100 * w.mean() / m.mean() if len(w) == SEASON_TOP and len(m) == SEASON_TOP else None
    return _per_ba(in_dir, f)


def peak_to_mean(in_dir=None):
    """The mean of the year's ten highest days as a percent of its mean day."""
    return _per_ba(in_dir, lambda s: 100 * s["value"].nlargest(TOP_DAYS).mean() / s["value"].mean())


def subba(in_dir):
    def build():
        parts = []
        for y in YEARS:
            try:
                parts.append(hm.series(f"eia930_subba_demand_hourly_{y}", in_dir, variables=["demand_mw"], extra=("node",)))
            except common.NoData:
                continue
        if not parts:
            raise common.NoData("eia930_subba_demand_hourly_<year>")
        d = pd.concat(parts, ignore_index=True).drop_duplicates(["entity", "ts_utc"])
        d = d[d["value"] > 0]
        d["parent"], d["code"] = d["entity"].str.split(":").str[1], d["entity"].str.split(":").str[2]
        d = d[d["parent"].isin(PARENT)]
        out = []
        for parent, g in d.groupby("parent"):
            local = g["ts"].dt.tz_convert(PARENT[parent][1])
            out.append(g.assign(year=local.dt.year.values, lhour=local.dt.hour.values))
        d = pd.concat(out, ignore_index=True)
        med = d.groupby(["entity", "year"])["value"].transform("median")
        return d[d["value"] <= med * 3]
    return hm._cached(("deep_subba", in_dir), build)


def _per_sub(in_dir, fn):
    rows, tables = [], {}
    d = subba(in_dir)
    for (parent, code), g in d.groupby(["parent", "code"]):
        grid = PARENT[parent][0]
        region = f"{grid}_sub_{code}"
        name = str(g["node"].dropna().iloc[0]) if g["node"].notna().any() else code
        words = f"{name.split(' (')[0]} ({code}, a sub-region of {parent})"
        for y, s in g.groupby("year"):
            if int(y) not in YEARS:
                continue
            v = fn(s)
            rows.append(hm._row(region, words, y, None if v is None else float(v), len(s)))
        tables[region] = [f"eia930_subba_demand_hourly_{y}" for y in YEARS]
    return {"rows": rows, "tables": tables}


def sub_p99(in_dir=None):
    """The year's 99th-percentile hour of a sub-region's demand (MW)."""
    return _per_sub(in_dir, lambda s: np.percentile(s["value"], 99, method="averaged_inverted_cdf"))


def sub_mean(in_dir=None):
    """The year's mean hour of a sub-region's demand (MW)."""
    return _per_sub(in_dir, lambda s: s["value"].mean())


def sub_night_share(in_dir=None):
    """A sub-region's mean demand from midnight to 6 AM local as a percent of its all-hours mean."""
    return _per_sub(in_dir, lambda s: 100 * s.loc[s["lhour"].between(*NIGHT), "value"].mean() / s["value"].mean())


def sub_load_factor(in_dir=None):
    """A sub-region's mean hour as a percent of its 99th-percentile hour."""
    return _per_sub(in_dir, lambda s: 100 * s["value"].mean() / np.percentile(s["value"], 99, method="averaged_inverted_cdf"))


# ---------------------------------------------------------------------------------------------------------------------
# the reproduction scripts
# ---------------------------------------------------------------------------------------------------------------------
PY_DAILY = '''"""ERW findings hunt (chain 164): reproduce candidate {name} for {region} from the ERW's public table.

    python {{this file}} <eia930_daily_demand.csv>

{label}, by calendar year, for EIA-930 respondent {ba}. A day under a third or over three times its year's median is
dropped as a fault of the report (the weekly hunt's rule).
"""
import sys

import pandas as pd

with open(sys.argv[1], encoding="utf-8") as f:
    skip = 0
    for line in f:
        if not line.startswith("#"):
            break
        skip += 1
d = pd.read_csv(sys.argv[1], skiprows=skip, usecols=["entity", "variable", "ts_utc", "value"], dtype=str)
d = d[(d["entity"] == "eia930:{ba}") & (d["variable"] == "demand_mwh")].copy()
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d[d["value"] > 0].drop_duplicates(["entity", "ts_utc"])
d["year"], d["month"] = d["ts_utc"].str[:4].astype(int), d["ts_utc"].str[5:7].astype(int)
med = d.groupby("year")["value"].transform("median")
d = d[(d["value"] >= med / 3) & (d["value"] <= med * 3)]
for y, s in d.groupby("year"):
{body}
'''

PY_DAILY_BODY = {
    "top_days": "    print(y, round(float(s['value'].nlargest(10).mean() / 1000), 6), len(s))",
    "mean_day": "    print(y, round(float(s['value'].mean() / 1000), 6), len(s))",
    "peak_to_mean": "    print(y, round(float(100 * s['value'].nlargest(10).mean() / s['value'].mean()), 6), len(s))",
    "winter_vs_summer": ("    w = s.loc[s['month'].isin([1, 2, 12]), 'value'].nlargest(5)\n    m = s.loc[s['month'].isin([6, 7, 8]), 'value'].nlargest(5)\n"
                         "    if len(w) == 5 and len(m) == 5:\n        print(y, round(float(100 * w.mean() / m.mean()), 6), len(s))"),
}

PY_SUB = '''"""ERW findings hunt (chain 164): reproduce candidate {name} for {region} from the ERW's public tables.

    python {{this file}} <eia930_subba_demand_hourly_2019.csv> ... <eia930_subba_demand_hourly_2025.csv>

{label}, by local year ({tz}), for EIA-930 sub-region {entity}. An hour at or below zero, or over three times its
year's median, is dropped as a fault of the report.
"""
import sys

import numpy as np
import pandas as pd


def read(path):
    with open(path, encoding="utf-8") as f:
        skip = 0
        for line in f:
            if not line.startswith("#"):
                break
            skip += 1
    d = pd.read_csv(path, skiprows=skip, usecols=["entity", "variable", "ts_utc", "value"], dtype=str)
    return d[(d["entity"] == "{entity}") & (d["variable"] == "demand_mw")]


d = pd.concat([read(p) for p in sys.argv[1:]], ignore_index=True).drop_duplicates(["entity", "ts_utc"])
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d[d["value"] > 0].copy()
local = pd.to_datetime(d["ts_utc"], format="%Y-%m-%dT%H:%M:%SZ", utc=True).dt.tz_convert("{tz}")
d["year"], d["lhour"] = local.dt.year, local.dt.hour
med = d.groupby("year")["value"].transform("median")
d = d[d["value"] <= med * 3]
for y, s in d.groupby("year"):
    if 2019 <= y <= 2025:
{body}
'''

PY_SUB_BODY = {
    "sub_p99": "        print(y, round(float(np.percentile(s['value'], 99, method='averaged_inverted_cdf')), 6), len(s))",
    "sub_mean": "        print(y, round(float(s['value'].mean()), 6), len(s))",
    "sub_night_share": "        print(y, round(float(100 * s.loc[s['lhour'].between(0, 5), 'value'].mean() / s['value'].mean()), 6), len(s))",
    "sub_load_factor": "        print(y, round(float(100 * s['value'].mean() / np.percentile(s['value'], 99, method='averaged_inverted_cdf')), 6), len(s))",
}


def _ba_of(region):
    return next(k for k, (r, _) in BA.items() if r == region)


def _sub_of(region):
    grid, code = region.split("_sub_", 1)
    parent = next(k for k, v in PARENT.items() if v[0] == grid)
    return parent, code


def reproduce_py(name, region):
    P = next(p for p in CANDIDATES if p["name"] == name)
    label = P["label"][0].upper() + P["label"][1:]
    if name in PY_DAILY_BODY:
        return PY_DAILY.format(name=name, region=region, label=label, ba=_ba_of(region), body=PY_DAILY_BODY[name])
    parent, code = _sub_of(region)
    return PY_SUB.format(name=name, region=region, label=label, tz=PARENT[parent][1], entity=f"eia930_subba:{parent}:{code}", body=PY_SUB_BODY[name])


def _dst(var, off):
    return [f"generate int y_utc = year(dofc({var}))", "generate int mar1 = mdy(3, 1, y_utc)", "generate int dst_start = mar1 + mod(7 - dow(mar1), 7) + 7",
            "generate int nov1 = mdy(11, 1, y_utc)", "generate int dst_end = nov1 + mod(7 - dow(nov1), 7)",
            f"generate byte dst = {var} >= cofd(dst_start) + msofhours({2 + off}) & {var} < cofd(dst_end) + msofhours({1 + off})",
            f"generate double t_local = {var} - msofhours({off}) + dst * msofhours(1)"]


def reproduce_do(name, region):
    head = [f"* ERW findings hunt (chain 164): reproduce candidate {name} for {region} from the ERW's public tables.",
            "* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.",
            "clear all"]
    if name in PY_DAILY_BODY:
        ba = _ba_of(region)
        lines = head + ['import delimited "eia930_daily_demand.csv", varnames(1) stringcols(_all) clear',
                        f'keep if entity == "eia930:{ba}" & variable == "demand_mwh"', "destring value, replace force", "keep if value > 0 & !missing(value)",
                        "duplicates drop entity ts_utc, force", "generate int year = real(substr(ts_utc, 1, 4))", "generate int month = real(substr(ts_utc, 6, 2))",
                        "bysort year: egen double med = median(value)", "keep if value >= med / 3 & value <= med * 3"]
        if name == "mean_day":
            lines += ["collapse (mean) measure = value (count) n = value, by(year)", "replace measure = measure / 1000"]
        elif name in ("top_days", "peak_to_mean"):
            lines += ["generate double neg_value = -value", "bysort year (neg_value): generate long rank = _n", "by year: egen double top = mean(cond(rank <= 10, value, .))",
                      "by year: egen double avg = mean(value)", "by year: generate long n = _N", "by year: keep if _n == 1",
                      "generate double measure = " + ("top / 1000" if name == "top_days" else "100 * top / avg")]
        else:
            lines += ["generate byte season = cond(inlist(month, 1, 2, 12), 1, cond(inlist(month, 6, 7, 8), 2, 0))", "bysort year: generate long n = _N",
                      "generate double neg_value = -value", "bysort year season (neg_value): generate long rank = _n", "keep if season > 0 & rank <= 5",
                      "collapse (mean) top = value (count) k = value (firstnm) n, by(year season)", "keep if k == 5",
                      "reshape wide top k, i(year) j(season)", "drop if missing(top1) | missing(top2)", "generate double measure = 100 * top1 / top2"]
    else:
        parent, code = _sub_of(region)
        off = PARENT[parent][2]
        lines = head[:]
        for i, y in enumerate(YEARS):
            lines += [f'import delimited "eia930_subba_demand_hourly_{y}.csv", varnames(1) stringcols(_all) clear',
                      f'keep if entity == "eia930_subba:{parent}:{code}" & variable == "demand_mw"', "keep entity ts_utc value"]
            if i > 0:
                lines += ["append using subba_hours"]
            lines += ["save subba_hours, replace"]
        lines += ["duplicates drop entity ts_utc, force", "destring value, replace force", "keep if value > 0 & !missing(value)",
                  'generate double t_utc = clock(subinstr(subinstr(ts_utc, "T", " ", 1), "Z", "", 1), "YMDhms")'] + _dst("t_utc", off) + [
                  "generate int year = year(dofc(t_local))", "generate int lhour = hh(t_local)", "keep if year >= 2019 & year <= 2025",
                  "bysort year: egen double med = median(value)", "keep if value <= med * 3"]
        if name == "sub_mean":
            lines += ["collapse (mean) measure = value (count) n = value, by(year)"]
        elif name == "sub_p99":
            lines += ["collapse (p99) measure = value (count) n = value, by(year)"]
        elif name == "sub_load_factor":
            lines += ["collapse (mean) avg = value (p99) top = value (count) n = value, by(year)", "generate double measure = 100 * avg / top"]
        else:
            lines += ["generate double night = value if inrange(lhour, 0, 5)", "collapse (mean) avg = value (mean) nig = night (count) n = value, by(year)",
                      "generate double measure = 100 * nig / avg"]
    lines += ["sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
CANDIDATES = [
    C("top_days", FAMILY, top_days, "GWh a day", 1, 330, 5.0, "THE YEAR'S TOP DAYS OF DEMAND",
      "the mean of the year's ten highest days of demand",
      lambda w: f"the mean of the ten highest days of demand in {w}",
      "EIA-930 as the respondent reported it, by EIA's Eastern day; days of reporting faults are dropped by a rule, and a respondent that changed its footprint changes its demand.",
      reproduce("top_days"), consequence=3),
    C("mean_day", FAMILY, mean_day, "GWh a day", 1, 330, 5.0, "THE YEAR'S MEAN DAY OF DEMAND",
      "the year's mean day of demand", lambda w: f"the mean day of demand in {w}",
      "Not adjusted for weather; EIA-930 as reported, and a respondent that changed its footprint changes its demand.",
      reproduce("mean_day"), consequence=3),
    C("winter_vs_summer", FAMILY, winter_vs_summer, "percent of the summer top days", 1, 330, 5.0, "WINTER'S TOP DAYS AGAINST SUMMER'S",
      "the mean of the year's five highest winter days (January, February, December) as a percent of its five highest summer days (June to August)",
      lambda w: f"the mean of the five highest winter days of demand in {w}, against its five highest summer days,",
      "Five days a season: one cold spell or one heat wave can carry a year, and the year's December is not the same winter as its January.",
      reproduce("winter_vs_summer"), consequence=3),
    C("peak_to_mean", FAMILY, peak_to_mean, "percent of the mean day", 1, 330, 3.0, "HOW PEAKY THE YEAR IS",
      "the mean of the year's ten highest days as a percent of its mean day",
      lambda w: f"the mean of the ten highest days of demand in {w}",
      "Days, not hours: an hourly peak can move without the day's total moving.",
      reproduce("peak_to_mean"), consequence=2),
    C("sub_p99", FAMILY, sub_p99, "MW", 0, 8000, 100.0, "A SUB-REGION'S PEAK HOURS",
      "the year's 99th-percentile hour of the sub-region's demand",
      lambda w: f"the 99th-percentile hour of demand in {w}",
      "EIA-930 sub-region data as the operator reported it; an hour over three times its year's median is dropped as a fault, and a change of the sub-region's footprint changes its demand.",
      reproduce("sub_p99"), consequence=3),
    C("sub_mean", FAMILY, sub_mean, "MW", 0, 8000, 100.0, "A SUB-REGION'S MEAN HOUR",
      "the year's mean hour of the sub-region's demand",
      lambda w: f"the mean hour of demand in {w}",
      "Not adjusted for weather; EIA-930 sub-region data as reported, and a change of the sub-region's footprint changes its demand.",
      reproduce("sub_mean"), consequence=3),
    C("sub_night_share", FAMILY, sub_night_share, "percent of the all-hours mean", 1, 8000, 3.0, "A SUB-REGION'S NIGHT",
      "the sub-region's mean demand from midnight to 6 AM local as a percent of its all-hours mean",
      lambda w: f"the mean night demand (midnight to 6 AM) in {w}",
      "A ratio of two means: demand that grows in every hour alike leaves it where it was, and demand that grows by day lowers it.",
      reproduce("sub_night_share"), consequence=2),
    C("sub_load_factor", FAMILY, sub_load_factor, "percent of the 99th-percentile hour", 1, 8000, 3.0, "A SUB-REGION'S LOAD FACTOR",
      "the sub-region's mean hour as a percent of its 99th-percentile hour",
      lambda w: f"the mean hour of demand in {w}, against its 99th-percentile hour,",
      "The 99th percentile, not the year's single peak; a ratio, so it rises whether the mean grows or the peak hours shrink.",
      reproduce("sub_load_factor"), consequence=2),
]


for _P in CANDIDATES:
    if _P["name"] in ("top_days", "mean_day", "sub_p99", "sub_mean"):
        _P["rank"] = lambda c: abs(c["change"])   # session 3004: the largest change first, not the steadiest small one


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt, family demand (chain 164)")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--only", default=None)
    ap.add_argument("--replace", action="store_true", help="correct the open drafts of the same claims in place (session 3019)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    cands = [P for P in CANDIDATES if not a.only or P["name"] == a.only]
    builder.run(FAMILY, cands, a.in_dir, dry_run=not a.load, replace=a.replace)
    return 0


if __name__ == "__main__":
    sys.exit(main())
