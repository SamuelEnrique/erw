#!/usr/bin/env python3
"""The findings hunt over the whole warehouse (chain 164), family "queues_deals_datacenters", first part: the queues (session 3009).

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-06.md. Public sources:

    iso_queue_snapshot_summary   the ERW's summary of the ISOs' own queue snapshots, by grid and year (CAISO and ERCOT;
                                 SPP is held by a ruling): MW entered, and the median months from request to in-service
    lbnl_interconnection_queue   Berkeley Lab's Queued Up (CC BY 4.0), one row a request across the country: the request
                                 date, the online date, the withdrawal date, the type, the MW and the region

A year of requests is one observation of its year (as session 3006 found for annual totals): the count of requests
grows and is no test of a year being whole. A median of months needs at least MIN_PROJECTS projects in its year.
Regions of MISO, NYISO, ISO-NE and SPP are never drafted (a license is needed or a ruling holds), whoever published the
rows; Berkeley Lab's other regions are kept (PJM, CAISO, ERCOT, the West and the Southeast outside the ISOs).

    python warehouse/analysis/findings/deep/queues.py --dry-run
    python warehouse/analysis/findings/deep/queues.py --load
"""

import argparse
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
sys.path.insert(0, HERE)
import builder  # noqa: E402
import findings_common as common  # noqa: E402
import hunt_measures as hm  # noqa: E402

FAMILY = "queues_deals_datacenters"
GRIDS = {"iso_queue:caiso": ("caiso_queue", "CAISO's queue"), "iso_queue:ercot": ("ercot_queue", "ERCOT's queue")}
REGION = {"PJM": ("pjm_lbnl", "PJM"), "CAISO": ("caiso_lbnl", "CAISO"), "ERCOT": ("ercot_lbnl", "ERCOT"), "West": ("west_lbnl", "the West outside CAISO"),
          "Southeast": ("southeast_lbnl", "the Southeast"), "MISO": ("miso_lbnl", "MISO"), "SPP": ("spp_lbnl", "SPP"), "NYISO": ("nyiso_lbnl", "NYISO"),
          "ISO-NE": ("isone_lbnl", "ISO-NE")}
TYPES = {"Solar": "solar", "Battery": "battery", "Wind": "wind", "Gas": "gas"}
MIN_PROJECTS = 10
FIRST, LAST = 2005, 2024


def _summary(in_dir, var):
    d = hm.series("iso_queue_snapshot_summary", in_dir, variables=[var], entities=list(GRIDS))
    rows, tables = [], {}
    for ent, g in d.groupby("entity"):
        region, words = GRIDS[ent]
        region = f"{region}_{var}"
        for _, r in g.iterrows():
            if FIRST <= r["ts"].year <= LAST + 1:
                rows.append(hm._row(region, words, r["ts"].year, float(r["value"]), 1))
        tables[region] = ["iso_queue_snapshot_summary"]
    return {"rows": rows, "tables": tables}


def entered_mw(in_dir=None):
    """The MW of the requests that entered the grid's queue in the year (the ISO's own snapshot)."""
    return _summary(in_dir, "entered_mw")


def months_to_service(in_dir=None):
    """The median months from request to in-service of the requests that entered service in the year (the ISO's own snapshot)."""
    return _summary(in_dir, "median_months_to_in_service")


def lbnl(in_dir):
    def build():
        d = common.read_table("lbnl_interconnection_queue", in_dir, usecols=["entity_id", "q_date", "on_date", "wd_date", "q_status", "region", "type_clean", "mw_1", "q_year"])
        for c in ("q_date", "on_date", "wd_date"):
            d[c] = pd.to_datetime(d[c], errors="coerce")
        d["mw"], d["q_year"] = pd.to_numeric(d["mw_1"], errors="coerce"), pd.to_numeric(d["q_year"], errors="coerce")
        return d
    return hm._cached(("deep_lbnl", in_dir), build)


def months_by_region(in_dir=None):
    """By region and the US: the median months from request to online of the projects that came online in the year
    (Berkeley Lab's dates), years with at least ten such projects."""
    d = lbnl(in_dir).dropna(subset=["q_date", "on_date"])
    d = d[d["on_date"] >= d["q_date"]]
    d = d.assign(months=(d["on_date"] - d["q_date"]).dt.days / 30.4375, year=d["on_date"].dt.year)
    rows, tables = [], {}
    for name, g in [("US", d)] + list(d[d["region"].isin(REGION)].groupby("region")):
        region, words = ("us_lbnl", "the United States") if name == "US" else REGION[name]
        region = f"{region}_months"
        for y, s in g.groupby("year"):
            if FIRST <= y <= LAST and len(s) >= MIN_PROJECTS:
                rows.append(hm._row(region, words, y, float(s["months"].median()), 1))
        tables[region] = ["lbnl_interconnection_queue"]
    return {"rows": rows, "tables": tables}


def _typed(d, typ):
    return d[d["type_clean"] == typ]


def months_by_type(in_dir=None):
    """By type (solar, batteries, wind, gas), US: the median months from request to online of the projects that came
    online in the year, years with at least ten such projects (session 3011)."""
    d = lbnl(in_dir).dropna(subset=["q_date", "on_date"])
    d = d[d["on_date"] >= d["q_date"]]
    d = d.assign(months=(d["on_date"] - d["q_date"]).dt.days / 30.4375, year=d["on_date"].dt.year)
    rows, tables = [], {}
    for typ, key in TYPES.items():
        region = f"us_type_{key}_months"
        for y, s in _typed(d, typ).groupby("year"):
            if FIRST <= y <= LAST and len(s) >= MIN_PROJECTS:
                rows.append(hm._row(region, f"{key} projects in the United States", y, float(s["months"].median()), 1))
        tables[region] = ["lbnl_interconnection_queue"]
    return {"rows": rows, "tables": tables}


def withdrawn_by_type(in_dir=None):
    """By type, US: the MW withdrawn in the year as a percent of the MW withdrawn or brought online in it (session 3011)."""
    d = lbnl(in_dir).dropna(subset=["mw"])
    rows, tables = [], {}
    for typ, key in TYPES.items():
        g = _typed(d, typ)
        ob = g.dropna(subset=["on_date"]).groupby(g["on_date"].dt.year)["mw"].sum()
        wb = g.dropna(subset=["wd_date"]).groupby(g["wd_date"].dt.year)["mw"].sum()
        region = f"us_type_{key}_wd"
        for y in range(FIRST, LAST + 1):
            if ob.get(y, 0.0) > 0 and wb.get(y, 0.0) > 0:
                rows.append(hm._row(region, f"{key} projects in the United States", y, float(100 * wb[y] / (ob[y] + wb[y])), 1))
        tables[region] = ["lbnl_interconnection_queue"]
    return {"rows": rows, "tables": tables}


def request_size(in_dir=None):
    """By type, US: the median MW of the requests that entered a queue in the year, years with at least ten (session 3011)."""
    d = lbnl(in_dir).dropna(subset=["mw", "q_year"])
    rows, tables = [], {}
    for typ, key in TYPES.items():
        region = f"us_type_{key}_size"
        for y, s in _typed(d, typ).groupby("q_year"):
            if FIRST <= y <= LAST and len(s) >= MIN_PROJECTS:
                rows.append(hm._row(region, f"{key} requests in the United States", y, float(s["mw"].median()), 1))
        tables[region] = ["lbnl_interconnection_queue"]
    return {"rows": rows, "tables": tables}


def requested_by_type(in_dir=None):
    """The US MW requested in the year (Berkeley Lab's queue year), by type: solar, batteries, wind, gas."""
    d = lbnl(in_dir).dropna(subset=["mw", "q_year"])
    d = d[d["type_clean"].isin(TYPES)]
    rows, tables = [], {}
    for typ, g in d.groupby("type_clean"):
        region = f"us_req_{TYPES[typ]}"
        by = g.groupby("q_year")["mw"].sum()
        for y in range(FIRST, LAST + 1):
            rows.append(hm._row(region, f"{TYPES[typ]} requests, the United States", y, float(by.get(y, 0.0)), 1))
        tables[region] = ["lbnl_interconnection_queue"]
    return {"rows": rows, "tables": tables}


def storage_share(in_dir=None):
    """Batteries' share of the US MW requested in the year (percent), Berkeley Lab's types."""
    d = lbnl(in_dir).dropna(subset=["mw", "q_year"])
    tot = d.groupby("q_year")["mw"].sum()
    bat = d[d["type_clean"] == "Battery"].groupby("q_year")["mw"].sum()
    rows = [hm._row("us_req_battery_share", "requests in the United States", y, float(100 * bat.get(y, 0.0) / tot[y]), 1)
            for y in range(FIRST, LAST + 1) if tot.get(y, 0) > 0]
    return {"rows": rows, "tables": {"us_req_battery_share": ["lbnl_interconnection_queue"]}}


def hybrid_share(in_dir=None):
    """By region and the US: the percent of the solar MW requested in the year whose request also lists a battery."""
    d = common.read_table("lbnl_interconnection_queue", in_dir, usecols=["type_1", "type_2", "type_3", "region", "mw_1", "q_year"])
    d["mw"], d["q_year"] = pd.to_numeric(d["mw_1"], errors="coerce"), pd.to_numeric(d["q_year"], errors="coerce")
    d = d.dropna(subset=["mw", "q_year"])
    d = d[d["type_1"] == "Solar"]
    d["paired"] = (d["type_2"] == "Battery") | (d["type_3"] == "Battery")
    rows, tables = [], {}
    for name, g in [("US", d)] + list(d[d["region"].isin(REGION)].groupby("region")):
        region, words = ("us_lbnl", "the United States") if name == "US" else REGION[name]
        region = f"{region}_hybrid"
        tot, par = g.groupby("q_year")["mw"].sum(), g[g["paired"]].groupby("q_year")["mw"].sum()
        for y in range(FIRST, LAST + 1):
            if tot.get(y, 0) > 0:
                rows.append(hm._row(region, words, y, float(100 * par.get(y, 0.0) / tot[y]), 1))
        tables[region] = ["lbnl_interconnection_queue"]
    return {"rows": rows, "tables": tables}


def withdrawn_share(in_dir=None):
    """By region and the US: the MW withdrawn in the year as a percent of the MW withdrawn or brought online in it."""
    d = lbnl(in_dir).dropna(subset=["mw"])
    on = d.dropna(subset=["on_date"]).assign(year=lambda x: x["on_date"].dt.year)
    wd = d.dropna(subset=["wd_date"]).assign(year=lambda x: x["wd_date"].dt.year)
    rows, tables = [], {}
    for name in ["US"] + list(REGION):
        o = on if name == "US" else on[on["region"] == name]
        w = wd if name == "US" else wd[wd["region"] == name]
        region, words = ("us_lbnl", "the United States") if name == "US" else REGION[name]
        region = f"{region}_wd"
        ob, wb = o.groupby("year")["mw"].sum(), w.groupby("year")["mw"].sum()
        for y in range(FIRST, LAST + 1):
            # session 3009: a year counts when both exits are held in it; a provider that lists no withdrawal dates in its
            # early years (ERCOT before 2013) would show none withdrawn
            if ob.get(y, 0.0) > 0 and wb.get(y, 0.0) > 0:
                rows.append(hm._row(region, words, y, float(100 * wb[y] / (ob[y] + wb[y])), 1))
        tables[region] = ["lbnl_interconnection_queue"]
    return {"rows": rows, "tables": tables}


# ---------------------------------------------------------------------------------------------------------------------
# the reproduction scripts
# ---------------------------------------------------------------------------------------------------------------------
PY_HEAD = '''"""ERW findings hunt (chain 164): reproduce candidate {name} for {region} from the ERW's public table.

    python {{this file}} <{table}.csv>

{label}.
"""
import sys

import pandas as pd

with open(sys.argv[1], encoding="utf-8") as f:
    skip = 0
    for line in f:
        if not line.startswith("#"):
            break
        skip += 1
d = pd.read_csv(sys.argv[1], skiprows=skip, dtype=str)
'''
PY_LBNL = ("for c in ('q_date', 'on_date', 'wd_date'):\n    d[c] = pd.to_datetime(d[c], errors='coerce')\n"
           "d['mw'], d['q_year'] = pd.to_numeric(d['mw_1'], errors='coerce'), pd.to_numeric(d['q_year'], errors='coerce')\n")


def _lbnl_name(region):
    key = region.rsplit("_", 1)[0]
    return "US" if key == "us_lbnl" else next(k for k, v in REGION.items() if v[0] == key)


def _type_of(region):
    key = region.split("_")[2]
    return next(k for k, v in TYPES.items() if v == key)


def reproduce_py(name, region):
    if name == "request_size":
        typ = _type_of(region)
        P = next(p for p in CANDIDATES if p["name"] == name)
        return (PY_HEAD.format(name=name, region=region, table="lbnl_interconnection_queue", label=P["label"][0].upper() + P["label"][1:]) + PY_LBNL
                + f"d = d.dropna(subset=['mw', 'q_year'])\nd = d[d['type_clean'] == {typ!r}]\n"
                + f"for y, s in d.groupby('q_year'):\n    if {FIRST} <= y <= {LAST} and len(s) >= {MIN_PROJECTS}:\n        print(int(y), round(float(s['mw'].median()), 6), 1)\n")
    if name in ("months_by_type", "withdrawn_by_type"):
        typ = _type_of(region)
        alias = {"months_by_type": "months_by_region", "withdrawn_by_type": "withdrawn_share"}[name]
        text = reproduce_py(alias, "us_lbnl_" + ("months" if name == "months_by_type" else "wd"))
        P = next(p for p in CANDIDATES if p["name"] == name)
        Q = next(p for p in CANDIDATES if p["name"] == alias)
        text = text.replace(f"candidate {alias} for us_lbnl_", f"candidate {name} for {region} (us_lbnl_")
        text = text.replace(Q["label"][0].upper() + Q["label"][1:], P["label"][0].upper() + P["label"][1:])
        marker = "d['mw'], d['q_year'] = pd.to_numeric(d['mw_1'], errors='coerce'), pd.to_numeric(d['q_year'], errors='coerce')\n"
        assert marker in text
        return text.replace(marker, marker + f"d = d[d['type_clean'] == {typ!r}]\n", 1)
    P = next(p for p in CANDIDATES if p["name"] == name)
    label = P["label"][0].upper() + P["label"][1:]
    if name in ("entered_mw", "months_to_service"):
        var = "entered_mw" if name == "entered_mw" else "median_months_to_in_service"
        ent = next(k for k, v in GRIDS.items() if region == f"{v[0]}_{var}")
        body = (f"d = d[(d['entity'] == {ent!r}) & (d['variable'] == {var!r})]\nd['value'] = pd.to_numeric(d['value'], errors='coerce')\n"
                f"for _, r in d.dropna(subset=['value']).iterrows():\n    y = int(r['ts_utc'][:4])\n    if {FIRST} <= y <= {LAST + 1}:\n        print(y, round(float(r['value']), 6), 1)\n")
        return PY_HEAD.format(name=name, region=region, table="iso_queue_snapshot_summary", label=label) + body
    head = PY_HEAD.format(name=name, region=region, table="lbnl_interconnection_queue", label=label) + PY_LBNL
    if name == "months_by_region":
        rn = _lbnl_name(region)
        filt = "" if rn == "US" else f"d = d[d['region'] == {rn!r}]\n"
        body = (filt + "d = d.dropna(subset=['q_date', 'on_date'])\nd = d[d['on_date'] >= d['q_date']]\n"
                "d['months'], d['year'] = (d['on_date'] - d['q_date']).dt.days / 30.4375, d['on_date'].dt.year\n"
                f"for y, s in d.groupby('year'):\n    if {FIRST} <= y <= {LAST} and len(s) >= {MIN_PROJECTS}:\n        print(int(y), round(float(s['months'].median()), 6), 1)\n")
    elif name == "requested_by_type":
        typ = next(k for k, v in TYPES.items() if region == f"us_req_{v}")
        body = (f"d = d.dropna(subset=['mw', 'q_year'])\nby = d[d['type_clean'] == {typ!r}].groupby('q_year')['mw'].sum()\n"
                f"for y in range({FIRST}, {LAST + 1}):\n    print(y, round(float(by.get(y, 0.0)), 6), 1)\n")
    elif name == "storage_share":
        body = ("d = d.dropna(subset=['mw', 'q_year'])\ntot = d.groupby('q_year')['mw'].sum()\nbat = d[d['type_clean'] == 'Battery'].groupby('q_year')['mw'].sum()\n"
                f"for y in range({FIRST}, {LAST + 1}):\n    if tot.get(y, 0) > 0:\n        print(y, round(float(100 * bat.get(y, 0.0) / tot[y]), 6), 1)\n")
    elif name == "hybrid_share":
        rn = _lbnl_name(region)
        filt = "" if rn == "US" else f"d = d[d['region'] == {rn!r}]\n"
        body = (filt + "d = d.dropna(subset=['mw', 'q_year'])\nd = d[d['type_1'] == 'Solar']\nd['paired'] = (d['type_2'] == 'Battery') | (d['type_3'] == 'Battery')\n"
                "tot, par = d.groupby('q_year')['mw'].sum(), d[d['paired']].groupby('q_year')['mw'].sum()\n"
                f"for y in range({FIRST}, {LAST + 1}):\n    if tot.get(y, 0) > 0:\n        print(y, round(float(100 * par.get(y, 0.0) / tot[y]), 6), 1)\n")
    else:
        rn = _lbnl_name(region)
        filt = "" if rn == "US" else f"d = d[d['region'] == {rn!r}]\n"
        body = (filt + "d = d.dropna(subset=['mw'])\nob = d.dropna(subset=['on_date']).groupby(d['on_date'].dt.year)['mw'].sum()\n"
                "wb = d.dropna(subset=['wd_date']).groupby(d['wd_date'].dt.year)['mw'].sum()\n"
                f"for y in range({FIRST}, {LAST + 1}):\n    if ob.get(y, 0.0) > 0 and wb.get(y, 0.0) > 0:\n"
                "        print(y, round(float(100 * wb[y] / (ob[y] + wb[y])), 6), 1)\n")
    return head + body


def reproduce_do(name, region):
    if name == "request_size":
        typ = _type_of(region)
        return common.do_file([f"* ERW findings hunt (chain 164): reproduce candidate {name} for {region} from the ERW's public table.",
                               "* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.",
                               "clear all", 'import delimited "lbnl_interconnection_queue.csv", varnames(1) stringcols(_all) clear', "destring mw_1 q_year, replace force",
                               f'keep if type_clean == "{typ}" & !missing(mw_1) & !missing(q_year)', f"keep if inrange(q_year, {FIRST}, {LAST})",
                               "collapse (median) measure = mw_1 (count) k = mw_1, by(q_year)", f"keep if k >= {MIN_PROJECTS}", "rename q_year year", "generate byte n = 1",
                               "sort year", "list year measure n, noobs"])
    if name in ("months_by_type", "withdrawn_by_type"):
        typ = _type_of(region)
        alias = {"months_by_type": "months_by_region", "withdrawn_by_type": "withdrawn_share"}[name]
        text = reproduce_do(alias, "us_lbnl_" + ("months" if name == "months_by_type" else "wd"))
        text = text.replace(f"candidate {alias} for us_lbnl_", f"candidate {name} for {region} (us_lbnl_")
        marker = 'generate long wd = daily(substr(wd_date, 1, 10), "YMD")'
        assert marker in text
        return text.replace(marker, marker + f'\n\nkeep if type_clean == "{typ}"', 1)
    head = [f"* ERW findings hunt (chain 164): reproduce candidate {name} for {region} from the ERW's public table.",
            "* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.",
            "clear all"]
    if name in ("entered_mw", "months_to_service"):
        var = "entered_mw" if name == "entered_mw" else "median_months_to_in_service"
        ent = next(k for k, v in GRIDS.items() if region == f"{v[0]}_{var}")
        lines = head + ['import delimited "iso_queue_snapshot_summary.csv", varnames(1) stringcols(_all) clear', f'keep if entity == "{ent}" & variable == "{var}"',
                        "destring value, replace force", "drop if missing(value)", "generate int year = real(substr(ts_utc, 1, 4))",
                        f"keep if inrange(year, {FIRST}, {LAST + 1})", "rename value measure", "generate byte n = 1"]
    else:
        lines = head + ['import delimited "lbnl_interconnection_queue.csv", varnames(1) stringcols(_all) clear', "destring mw_1 q_year, replace force",
                        'generate long qd = daily(substr(q_date, 1, 10), "YMD")', 'generate long od = daily(substr(on_date, 1, 10), "YMD")',
                        'generate long wd = daily(substr(wd_date, 1, 10), "YMD")']
        if name == "months_by_region":
            rn = _lbnl_name(region)
            lines += ([] if rn == "US" else [f'keep if region == "{rn}"']) + [
                "keep if !missing(qd) & !missing(od) & od >= qd", "generate double months = (od - qd) / 30.4375", "generate int year = year(od)",
                f"keep if inrange(year, {FIRST}, {LAST})", "collapse (median) measure = months (count) k = months, by(year)", f"keep if k >= {MIN_PROJECTS}",
                "generate byte n = 1"]
        elif name == "requested_by_type":
            typ = next(k for k, v in TYPES.items() if region == f"us_req_{v}")
            lines += [f'keep if type_clean == "{typ}" & !missing(mw_1) & !missing(q_year)', f"keep if inrange(q_year, {FIRST}, {LAST})",
                      "collapse (sum) measure = mw_1, by(q_year)", "rename q_year year", "generate byte n = 1",
                      "* A year with no request is a year of zero MW, as the Python prints it."]
        elif name == "storage_share":
            lines += ["keep if !missing(mw_1) & !missing(q_year)", f"keep if inrange(q_year, {FIRST}, {LAST})",
                      'generate double bat = mw_1 if type_clean == "Battery"', "collapse (sum) tot = mw_1 (sum) bat, by(q_year)", "keep if tot > 0",
                      "generate double measure = 100 * bat / tot", "rename q_year year", "generate byte n = 1"]
        elif name == "hybrid_share":
            rn = _lbnl_name(region)
            lines += ([] if rn == "US" else [f'keep if region == "{rn}"']) + [
                'keep if type_1 == "Solar" & !missing(mw_1) & !missing(q_year)', f"keep if inrange(q_year, {FIRST}, {LAST})",
                'generate double par = mw_1 if type_2 == "Battery" | type_3 == "Battery"', "collapse (sum) tot = mw_1 (sum) par, by(q_year)",
                "keep if tot > 0", "generate double measure = 100 * par / tot", "rename q_year year", "generate byte n = 1"]
        else:
            rn = _lbnl_name(region)
            lines += ([] if rn == "US" else [f'keep if region == "{rn}"']) + [
                "keep if !missing(mw_1)", "generate int yon = year(od)", "generate int ywd = year(wd)", "preserve",
                "keep if !missing(yon)", "collapse (sum) online = mw_1, by(yon)", "rename yon year", "save lbnl_online, replace", "restore",
                "keep if !missing(ywd)", "collapse (sum) withdrawn = mw_1, by(ywd)", "rename ywd year",
                "merge 1:1 year using lbnl_online, nogenerate", "replace online = 0 if missing(online)", "replace withdrawn = 0 if missing(withdrawn)",
                f"keep if inrange(year, {FIRST}, {LAST}) & online > 0 & withdrawn > 0", "generate double measure = 100 * withdrawn / (online + withdrawn)", "generate byte n = 1"]
    lines += ["sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
LIMIT_LBNL = ("Berkeley Lab's Queued Up as the ERW holds it (CC BY 4.0, Lawrence Berkeley National Laboratory and GridTracker); "
              "a request's dates are those its transmission provider published, and some providers list no withdrawal date.")
CANDIDATES = [
    C("months_by_region", FAMILY, months_by_region, "months", 1, 1, 6.0, "THE WAIT IN THE QUEUE",
      "the median months from request to online of the projects that came online in the year",
      lambda w: f"the median months from interconnection request to commercial operation in {w}",
      LIMIT_LBNL + " Only projects that came online are in the median, and a year needs at least ten of them.",
      reproduce("months_by_region"), first_words="the first year this measure counts", consequence=3),
    C("months_by_type", FAMILY, months_by_type, "months", 1, 1, 6.0, "THE WAIT, BY TYPE",
      "the median months from request to online of the projects of the type that came online in the year",
      lambda w: f"the median months from interconnection request to commercial operation of {w}",
      LIMIT_LBNL + " Only projects that came online are in the median, a year needs at least ten of them, and a hybrid counts as its first type.",
      reproduce("months_by_type"), first_words="the first year this measure counts", consequence=3),
    C("withdrawn_by_type", FAMILY, withdrawn_by_type, "percent of MW leaving the queue", 1, 1, 5.0, "WITHDRAWN, BY TYPE",
      "the MW of the type withdrawn in the year as a percent of the MW of the type withdrawn or brought online in it",
      lambda w: f"the share of the MW of {w} leaving the queue that was withdrawn rather than brought online",
      LIMIT_LBNL + " A year's exits mix requests of many queue years; a year counts when both exits are held in it; a hybrid counts as its first type.",
      reproduce("withdrawn_by_type"), first_words="the first year this measure counts", consequence=2),
    C("request_size", FAMILY, request_size, "MW", 1, 1, 10.0, "THE SIZE OF A REQUEST",
      "the median MW of the requests of the type that entered a queue in the year",
      lambda w: f"the median size of {w}",
      LIMIT_LBNL + " A request's MW is its first type's; a year needs at least ten requests of the type.",
      reproduce("request_size"), first_words="the first year this measure counts", consequence=2),
    C("requested_by_type", FAMILY, requested_by_type, "MW", 0, 1, 5000.0, "WHAT WAS ASKED FOR",
      "the US MW requested in the year, by type", lambda w: f"the MW of {w}",
      LIMIT_LBNL + " A request is counted in its queue year whatever became of it; hybrids are counted by their first type.",
      reproduce("requested_by_type"), first_words="the first year this measure counts", consequence=2),
    C("storage_share", FAMILY, storage_share, "percent of requested MW", 1, 1, 3.0, "BATTERIES IN THE QUEUE",
      "batteries' share of the US MW requested in the year", lambda w: "batteries' share of the MW requested in the United States",
      LIMIT_LBNL + " Hybrids are counted by their first type, so batteries paired with solar are mostly counted as solar.",
      reproduce("storage_share"), first_words="the first year this measure counts", consequence=3),
    C("hybrid_share", FAMILY, hybrid_share, "percent of solar MW requested", 1, 1, 5.0, "SOLAR PAIRED WITH BATTERIES",
      "the percent of the solar MW requested in the year whose request also lists a battery",
      lambda w: f"the share of the solar MW requested in {w} whose request also lists a battery",
      LIMIT_LBNL + " A request counts as paired when Berkeley Lab lists a battery as its second or third type; its MW is the solar part.",
      reproduce("hybrid_share"), first_words="the first year this measure counts", consequence=3),
    C("withdrawn_share", FAMILY, withdrawn_share, "percent of MW leaving the queue", 1, 1, 5.0, "WITHDRAWN, NOT BUILT",
      "the MW withdrawn in the year as a percent of the MW withdrawn or brought online in it",
      lambda w: f"the share of the MW leaving the queue in {w} that was withdrawn rather than brought online",
      LIMIT_LBNL + " A year's exits mix requests of many queue years; a year counts when both exits are held in it.",
      reproduce("withdrawn_share"), first_words="the first year this measure counts", consequence=3),
]
for _P in CANDIDATES:
    _P["rank_region"] = lambda r: 1e9 if r.startswith("us_") else 0.0
    if _P["name"] in ("requested_by_type", "months_by_type", "withdrawn_by_type", "request_size"):
        _P["max_per"] = 3                         # solar, batteries and gas: three stories of what was asked for


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt, family queues (chain 164)")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--only", default=None)
    ap.add_argument("--replace", action="store_true", help="session 3009: correct the open drafts of the same claims in place")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    cands = [P for P in CANDIDATES if not a.only or P["name"] == a.only]
    builder.run(FAMILY + "_queues", cands, a.in_dir, dry_run=not a.load, replace=a.replace)
    return 0


if __name__ == "__main__":
    sys.exit(main())
