#!/usr/bin/env python3
"""The findings hunt of chain 502 (session 8200 on): the shared readers of the EIA-930 hourly tables of 17 November 2026.

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-19.md. The tables (all public, EIA;
method docs/methods/eia930_region_hourly.md and docs/methods/region_weather.md):

    eia930_region_pair_hourly          each pair of EIA's regions with a tie, the hour's flow from the first to the second
    eia930_region_hourly               the thirteen regions: demand, net generation, total interchange, forecast
    eia930_ba_demand_hourly            every balancing authority: demand
    eia930_ba_supply_hourly            every balancing authority: net generation and total interchange
    eia930_ba_interchange_hourly_<y>   each tie between two balancing authorities, each side's report its own row
    region_weather_hourly              each region's temperature by hour, stations weighted by county population

The fault rules, the same in the module and in every reproduction script:
    flows (a pair's flow, a tie's report, a total interchange): an hour whose absolute value is more than three times
        its year's 99th percentile of absolute values (that series, that year) is dropped as a fault of the report;
    demand: an hour at or below zero, or more than three times its year's median (that series, that year), is dropped
        (the weekly hunt's rule for EIA-930 demand, applied by hour).

No model is called: every figure is computed here from the tables.
"""

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
import findings_common as common  # noqa: E402
import hunt_measures as hm  # noqa: E402

sys.path.insert(0, HERE)
import builder  # noqa: E402

builder.CHAIN = 502                                       # the drafts of this hunt name chain 502 and its plan
builder.METHOD = "docs/reviews/findings-hunt-plan-2026-11-19.md"

YEARS = list(range(2018, 2027))
CHUNK = 1_000_000
CAP = 3.0                      # three times the year's 99th percentile of absolute values
REG = {"CAL": "California", "CAR": "the Carolinas", "CENT": "the Central region", "FLA": "Florida", "MIDA": "the Mid-Atlantic",
       "MIDW": "the Midwest", "NE": "New England", "NW": "the Northwest", "NY": "New York", "SE": "the Southeast", "SW": "the Southwest",
       "TEN": "Tennessee", "TEX": "Texas", "CAN": "Canada", "MEX": "Mexico"}
REGIONS = ["CAL", "CAR", "CENT", "FLA", "MIDA", "MIDW", "NE", "NW", "NY", "SE", "SW", "TEN", "TEX"]
# EIA-930's balancing authorities by code, as EIA's reference table names them (the ones a draft may name)
BA = {"AEC": "PowerSouth Energy Cooperative", "AECI": "Associated Electric Cooperative", "AVA": "Avista", "AVRN": "Avangrid Renewables",
      "AZPS": "Arizona Public Service", "BANC": "the Balancing Authority of Northern California", "BPAT": "the Bonneville Power Administration",
      "CHPD": "Chelan County PUD", "CISO": "the California ISO", "CPLE": "Duke Energy Progress East", "CPLW": "Duke Energy Progress West",
      "DOPD": "Douglas County PUD", "DUK": "Duke Energy Carolinas", "EPE": "El Paso Electric", "ERCO": "ERCOT", "FMPP": "the Florida Municipal Power Pool",
      "FPC": "Duke Energy Florida", "FPL": "Florida Power and Light", "GCPD": "Grant County PUD", "GVL": "Gainesville Regional Utilities",
      "IID": "the Imperial Irrigation District", "IPCO": "Idaho Power", "ISNE": "ISO New England", "JEA": "JEA", "LDWP": "the Los Angeles Department of Water and Power",
      "LGEE": "LG&E and KU", "MISO": "MISO", "NEVP": "NV Energy (Nevada Power)", "NWMT": "NorthWestern Energy (Montana)", "NYIS": "the New York ISO",
      "PACE": "PacifiCorp East", "PACW": "PacifiCorp West", "PGE": "Portland General Electric", "PJM": "PJM", "PNM": "Public Service Company of New Mexico",
      "PSCO": "Public Service Company of Colorado", "PSEI": "Puget Sound Energy", "SC": "Santee Cooper", "SCEG": "Dominion Energy South Carolina",
      "SCL": "Seattle City Light", "SEC": "Seminole Electric Cooperative", "SEPA": "the Southeastern Power Administration", "SOCO": "Southern Company",
      "SPA": "the Southwestern Power Administration", "SRP": "the Salt River Project", "SWPP": "the Southwest Power Pool", "TAL": "the City of Tallahassee",
      "TEC": "Tampa Electric", "TEPC": "Tucson Electric Power", "TIDC": "the Turlock Irrigation District", "TPWR": "Tacoma Power",
      "TVA": "the Tennessee Valley Authority", "WACM": "WAPA's Rocky Mountain region", "WALC": "WAPA's Desert Southwest region",
      "WAUW": "WAPA's Upper Great Plains West region", "AESO": "Alberta's system operator", "BCHA": "BC Hydro", "HQT": "Hydro-Quebec",
      "IESO": "Ontario's IESO", "MHEB": "Manitoba Hydro", "NBSO": "New Brunswick's system operator", "SPC": "SaskPower", "CEN": "Mexico's CENACE",
      "CFE": "Mexico's CFE", "GRIF": "Griffith Energy", "HGMA": "New Harquahala", "DEAA": "Arlington Valley", "GWA": "NaturEner Power Watch",
      "WWA": "NaturEner Wind Watch", "YAD": "Alcoa Power Generating (Yadkin)", "EEI": "Electric Energy Inc.", "HST": "the City of Homestead",
      "NSB": "New Smyrna Beach", "GLHB": "GridLiance High Plains", "SIKE": "Sikeston Board of Municipal Utilities"}


def ba_words(code):
    return BA.get(code, f"balancing authority {code}")


def read(table, in_dir, cols, nums, keep=None):
    """A warehouse CSV read in chunks, the rows keep(chunk) selects, nums made numbers, ts_utc kept as text."""
    p = common.table_path(table, in_dir)
    parts = []
    for ch in pd.read_csv(p, skiprows=common.header_lines(p), usecols=cols, dtype=str, chunksize=CHUNK, keep_default_na=False):
        if keep is not None:
            ch = ch[keep(ch)]
        if not len(ch):
            continue
        ch = ch.copy()
        for c in nums:
            ch[c] = pd.to_numeric(ch[c], errors="coerce")
        parts.append(ch)
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=cols)


def drop_flow_faults(d, col, by):
    """Drop the hours whose |col| is more than CAP times their group's 99th percentile of |col| (numpy's linear rule)."""
    a = d[col].abs()
    p99 = a.groupby([d[k] for k in by]).transform(lambda s: np.nanpercentile(s, 99) if s.notna().any() else np.nan)
    return d[a <= CAP * p99]


def drop_demand_faults(d, col, by):
    d = d[d[col] > 0]
    med = d.groupby(by)[col].transform("median")
    return d[(d[col] <= 3 * med)]


def pairs(in_dir):
    """The region pairs, hourly: entity code (FIRST-SECOND), year, month, value and each side's report."""
    def build():
        d = read("eia930_region_pair_hourly", in_dir, ["entity", "ts_utc", "value", "x_first_report", "x_second_report"],
                 ["value", "x_first_report", "x_second_report"])
        d["pair"] = d.pop("entity").str.split(":").str[1]
        d["year"] = d["ts_utc"].str[:4].astype(int)
        d["month"] = d["ts_utc"].str[5:7].astype(int)
        return d.dropna(subset=["value"])
    return hm._cached(("c502_pairs", in_dir), build)


def region(in_dir, variables=("demand_mw", "total_interchange_mw")):
    """The thirteen regions, hourly, wide: one row an hour and region with a column per variable."""
    key = ("c502_region", in_dir, tuple(variables))

    def build():
        d = read("eia930_region_hourly", in_dir, ["entity", "variable", "ts_utc", "value"], ["value"], keep=lambda c: c["variable"].isin(variables))
        d["code"] = d.pop("entity").str.split(":").str[1]
        w = d.pivot_table(index=["code", "ts_utc"], columns="variable", values="value", aggfunc="first").reset_index()
        w["year"] = w["ts_utc"].str[:4].astype(int)
        w["month"] = w["ts_utc"].str[5:7].astype(int)
        return w
    return hm._cached(key, build)


def region_demand(in_dir):
    """Each region's demand by hour, summed from eia930_ba_demand_hourly (session 8201): the region table writes no
    demand for the Carolinas, the Northwest, the Southeast and the Southwest, nor for the Midwest before September 2022,
    because their generation-only authorities never file demand and its rule needs every authority. Here a region's
    hour is the sum of every authority the files place in the region (x_region) that files demand in that month, held
    only when all of them have a value after the demand fault rule (per authority and year). Columns: code, ts_utc,
    year, month, demand_mw, n_ba."""
    def build():
        d = read("eia930_ba_demand_hourly", in_dir, ["entity", "variable", "ts_utc", "value", "x_region"], ["value"],
                 keep=lambda c: c["variable"] == "demand_mw")
        d = d.dropna(subset=["value"])
        d["year"] = d["ts_utc"].str[:4].astype(int)
        d["ym"] = d["ts_utc"].str[:7]
        nset = d.groupby(["x_region", "ym"])["entity"].transform("nunique")
        d["nset"] = nset
        d = drop_demand_faults(d, "value", ["entity", "year"])
        g = d.groupby(["x_region", "ts_utc"])
        w = pd.DataFrame({"demand_mw": g["value"].sum(), "n_ba": g["value"].size(), "nset": g["nset"].first()}).reset_index()
        w = w[w["n_ba"] == w["nset"]].rename(columns={"x_region": "code"})
        w["year"] = w["ts_utc"].str[:4].astype(int)
        w["month"] = w["ts_utc"].str[5:7].astype(int)
        return w.drop(columns=["nset"])
    return hm._cached(("c502_region_demand", in_dir), build)


PY_REGION_DEMAND = '''def region_demand(path, code):
    """The region's demand by hour: the sum of every authority the files place in the region that files demand in the
    month, held only when all of them have a value after the demand fault rule (per authority and year)."""
    d = read(path, ["entity", "variable", "ts_utc", "value", "x_region"])
    d = d[(d["variable"] == "demand_mw") & (d["x_region"] == code)].copy()
    d["value"] = pd.to_numeric(d["value"], errors="coerce")
    d = d.dropna(subset=["value"])
    d["year"] = d["ts_utc"].str[:4].astype(int)
    d["nset"] = d.groupby(d["ts_utc"].str[:7])["entity"].transform("nunique")
    d = d[d["value"] > 0]
    d = d[d["value"] <= 3 * d.groupby(["entity", "year"])["value"].transform("median")]
    g = d.groupby("ts_utc")
    w = pd.DataFrame({"demand_mw": g["value"].sum(), "n_ba": g["value"].size(), "nset": g["nset"].first()}).reset_index()
    w = w[w["n_ba"] == w["nset"]]
    w["year"] = w["ts_utc"].str[:4].astype(int)
    return w[["ts_utc", "year", "demand_mw"]]

'''


def do_region_demand(code, out_name="demand"):
    """Stata lines: the region's demand by hour into the data in memory (ts_utc, year, demand), the module's rule."""
    return ['import delimited "eia930_ba_demand_hourly.csv", varnames(1) stringcols(_all) clear',
            f'keep if variable == "demand_mw" & x_region == "{code}"', "keep entity ts_utc value", "destring value, replace force", "drop if missing(value)",
            "generate int year = real(substr(ts_utc, 1, 4))", "generate str7 ym = substr(ts_utc, 1, 7)", "bysort ym entity: generate byte firstba = _n == 1",
            "bysort ym: egen nset = total(firstba)", "drop if value <= 0", "bysort entity year: egen double med = median(value)", "drop if value > 3 * med",
            f"collapse (sum) {out_name} = value (count) nba = value (first) nset year, by(ts_utc)", "keep if nba == nset", "drop nba nset"]


def ix_year(in_dir, year):
    """One year of the balancing authorities' reports on their ties: reporter, neighbour, ts_utc, value."""
    d = read(f"eia930_ba_interchange_hourly_{year}", in_dir, ["entity", "ts_utc", "value"], ["value"])
    e = d.pop("entity").str.split(":").str[1].str.split("-", n=1)
    d["rep"], d["nbr"] = e.str[0], e.str[1]
    return d.dropna(subset=["value"])


def ties(in_dir):
    """Every tie's yearly figures, read one year table at a time: for the lower-coded side's report and the other side's
    (sign turned, so both read as power from the lower code to the higher), the hours, the mean, the hours above and below
    zero after the fault rule; and where both sides are held in an hour, the mean absolute difference between them."""
    def build():
        out = []
        for y in YEARS:
            try:
                d = ix_year(in_dir, y)
            except common.NoData:
                continue
            d = d[d["ts_utc"].str[:4].astype(int) == y]
            lo = d["rep"] < d["nbr"]
            d["a"], d["b"] = np.where(lo, d["rep"], d["nbr"]), np.where(lo, d["nbr"], d["rep"])
            d["side"] = np.where(lo, "lo", "hi")
            d["v"] = np.where(lo, d["value"], -d["value"])
            d["year"] = y
            d = drop_flow_faults(d, "v", ["a", "b", "side"])
            g = d.groupby(["a", "b", "side"])["v"]
            agg = pd.DataFrame({"n": g.size(), "mean": g.mean(), "pos": g.apply(lambda s: int((s > 0).sum())), "neg": g.apply(lambda s: int((s < 0).sum()))}).reset_index()
            w = d.pivot_table(index=["a", "b", "ts_utc"], columns="side", values="v", aggfunc="first")
            if {"lo", "hi"} <= set(w.columns):
                w = w.dropna().reset_index()
                w["gap"] = (w["lo"] - w["hi"]).abs()
                gg = w.groupby(["a", "b"])["gap"].agg(["size", "mean"]).rename(columns={"size": "n_both", "mean": "gap"}).reset_index()
                agg = agg.merge(gg, on=["a", "b"], how="left")
            else:
                agg["n_both"], agg["gap"] = np.nan, np.nan
            agg["year"] = y
            out.append(agg)
        return pd.concat(out, ignore_index=True)
    return hm._cached(("c502_ties", in_dir), build)


def weather(in_dir):
    def build():
        d = read("region_weather_hourly", in_dir, ["entity", "variable", "ts_utc", "value"], ["value"], keep=lambda c: c["variable"] == "temperature_f")
        d["code"] = d.pop("entity").str.split(":").str[1]
        return d
    return hm._cached(("c502_weather", in_dir), build)


# ---------------------------------------------------------------------------------------------------------------------
# the reproduction scripts' common parts
# ---------------------------------------------------------------------------------------------------------------------
PY_READ = '''import sys

import numpy as np
import pandas as pd


def read(path, cols):
    with open(path, encoding="utf-8") as f:
        skip = 0
        for line in f:
            if not line.startswith("#"):
                break
            skip += 1
    return pd.read_csv(path, skiprows=skip, usecols=cols, dtype=str, keep_default_na=False)


def drop_flow_faults(d, col, by):
    a = d[col].abs()
    p99 = a.groupby([d[k] for k in by]).transform(lambda s: np.nanpercentile(s, 99))
    return d[a <= 3 * p99]

'''


def py_doc(name, region, tables, what):
    return (f'"""ERW findings hunt (chain 502): reproduce candidate {name} for {region} from the ERW\'s public tables.\n\n'
            f"    python {{this file}} {' '.join('<' + t + '.csv>' for t in tables)}\n\n{what}\n"
            "An hour whose absolute flow is more than three times its year's 99th percentile of absolute flows is dropped as a fault\n"
            "of the report; an hour of demand at or below zero or above three times its year's median is dropped the same way.\n"
            'Prints one line a year: the year, the figure, the hours it rests on.\n"""\n')


def do_head(name, region, tables):
    return [f"* ERW findings hunt (chain 502): reproduce candidate {name} for {region} from the ERW's public tables ({', '.join(tables)}).",
            "* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.",
            "* Faults: an hour whose absolute flow is more than three times its year's 99th percentile of absolute flows is dropped; an hour of demand at or below zero or above three times its year's median is dropped. Stata's percentile rule differs from numpy's in the last place, which moves no hour of these series across the line.",
            "clear all"]


def do_flow_faults(col, by="year"):
    return [f"generate double absflow = abs({col})", f"bysort {by}: egen double p99 = pctile(absflow), p(99)", "drop if absflow > 3 * p99", "drop absflow p99"]
