#!/usr/bin/env python3
"""The findings hunt over the whole warehouse (chain 164), family "queues_deals_datacenters", second part: datacenters (session 3010).

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-06.md. The ERW's own deal and project
tables (energy_deals, datacenter_projects, datacenter_facilities) begin in 2025 and cannot be tested by year; the
Census Bureau's series can (public: works of the U.S. government):

    census_c30_construction_monthly      the value of private construction put in place by month (USD, not seasonally
                                         adjusted): data centers from 2014, all private nonresidential, electric power
    census_cbp_hosting_annual            County Business Patterns for NAICS 518210 (computing infrastructure, data
                                         processing and hosting) by state, 2012 to 2023: employment, establishments, payroll
    census_qss_utilities_hosting_quarterly   the Quarterly Services Survey's revenue of NAICS 518 (USD)

A year of an annual series is one observation of its year; a year of a monthly or quarterly series is whole when it
holds all its months or quarters (its count is the observations).

    python warehouse/analysis/findings/deep/datacenters.py --dry-run
    python warehouse/analysis/findings/deep/datacenters.py --load
"""

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
sys.path.insert(0, HERE)
import builder  # noqa: E402
import findings_common as common  # noqa: E402
import generation  # noqa: E402
import hunt_measures as hm  # noqa: E402

FAMILY = "queues_deals_datacenters"
C30 = "census_c30_construction_monthly"
CBP = "census_cbp_hosting_annual"
QSS = "census_qss_utilities_hosting_quarterly"
STATES = generation.STATES


def _c30(in_dir, entities):
    d = hm.series(C30, in_dir, variables=["value_put_in_place"], entities=entities)
    return d.assign(year=d["ts_utc"].str[:4].astype(int))


def dc_construction(in_dir=None):
    """The value of private data center construction put in place over the year (USD billion)."""
    d = _c30(in_dir, ["census_c30:private:data_center"])
    rows = [hm._row("us_dc_build", "US private data center construction", y, float(s["value"].sum() / 1e9), len(s)) for y, s in d.groupby("year")]
    return {"rows": rows, "tables": {"us_dc_build": [C30]}}


def dc_share(in_dir=None):
    """Data centers' share of the value of private nonresidential construction put in place over the year (percent),
    the months that hold both."""
    d = _c30(in_dir, ["census_c30:private:data_center", "census_c30:private:nonresidential"])
    w = d.pivot_table(index=["year", "ts_utc"], columns="entity", values="value").dropna().reset_index()
    rows = [hm._row("us_dc_share", "US private nonresidential construction", y,
                    float(100 * s["census_c30:private:data_center"].sum() / s["census_c30:private:nonresidential"].sum()), len(s)) for y, s in w.groupby("year")]
    return {"rows": rows, "tables": {"us_dc_share": [C30]}}


def power_construction(in_dir=None):
    """The value of private electric power construction put in place over the year (USD billion)."""
    d = _c30(in_dir, ["census_c30:private:electric"])
    rows = [hm._row("us_power_build", "US private electric power construction", y, float(s["value"].sum() / 1e9), len(s)) for y, s in d.groupby("year")]
    return {"rows": rows, "tables": {"us_power_build": [C30]}}


def _cbp(in_dir, var, prefix, fn=None):
    d = hm.series(CBP, in_dir, variables=[var] if fn is None else ["annual_payroll", "employment"])
    d = d.assign(st=d["entity"].str.split(":").str[1].str.upper(), year=d["ts_utc"].str[:4].astype(int))
    rows, tables = [], {}
    for st, g in [("US", d)] + list(d.groupby("st")):
        region = f"{prefix}_{st}"
        if fn is None:
            by = g.groupby("year")["value"].sum()
        else:
            p = g.pivot_table(index=["year", "st"], columns="variable", values="value").dropna()
            by = p.groupby("year").apply(fn) if len(p) else {}
        for y, v in (by.items() if hasattr(by, "items") else []):
            rows.append(hm._row(region, STATES.get(st, st), y, float(v), 1))
        tables[region] = [CBP]
    return {"rows": rows, "tables": tables}


def hosting_jobs(in_dir=None):
    """Mid-March employment in NAICS 518210 establishments (County Business Patterns), the US and each state."""
    return _cbp(in_dir, "employment", "jobs518")


def hosting_sites(in_dir=None):
    """The number of NAICS 518210 establishments (County Business Patterns), the US and each state."""
    return _cbp(in_dir, "establishments", "est518")


def hosting_pay(in_dir=None):
    """Annual payroll per mid-March employee in NAICS 518210 (USD thousand), the US and each state."""
    return _cbp(in_dir, None, "pay518", fn=lambda p: p["annual_payroll"].sum() / p["employment"].sum() / 1000)


def hosting_revenue(in_dir=None):
    """The revenue of NAICS 518 (data processing, hosting and related services) over the year (USD billion), the
    Quarterly Services Survey, not seasonally adjusted."""
    d = hm.series(QSS, in_dir, variables=["total_revenue"], entities=["census_qss:518"])
    d = d.assign(year=d["ts_utc"].str[:4].astype(int))
    rows = [hm._row("us_rev518", "US data processing and hosting (NAICS 518)", y, float(s["value"].sum() / 1e9), len(s)) for y, s in d.groupby("year")]
    return {"rows": rows, "tables": {"us_rev518": [QSS]}}


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
d = pd.read_csv(sys.argv[1], skiprows=skip, usecols=["entity", "variable", "ts_utc", "value"], dtype=str)
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d.dropna(subset=["value"])
d["year"] = d["ts_utc"].str[:4].astype(int)
'''

BODY = {
    "dc_construction": ("d = d[(d['entity'] == 'census_c30:private:data_center') & (d['variable'] == 'value_put_in_place')]\n"
                        "for y, s in d.groupby('year'):\n    print(y, round(float(s['value'].sum() / 1e9), 6), len(s))\n"),
    "power_construction": ("d = d[(d['entity'] == 'census_c30:private:electric') & (d['variable'] == 'value_put_in_place')]\n"
                           "for y, s in d.groupby('year'):\n    print(y, round(float(s['value'].sum() / 1e9), 6), len(s))\n"),
    "dc_share": ("d = d[d['entity'].isin(['census_c30:private:data_center', 'census_c30:private:nonresidential']) & (d['variable'] == 'value_put_in_place')]\n"
                 "w = d.pivot_table(index=['year', 'ts_utc'], columns='entity', values='value').dropna().reset_index()\n"
                 "for y, s in w.groupby('year'):\n    print(y, round(float(100 * s['census_c30:private:data_center'].sum() / s['census_c30:private:nonresidential'].sum()), 6), len(s))\n"),
    "hosting_revenue": ("d = d[(d['entity'] == 'census_qss:518') & (d['variable'] == 'total_revenue')]\n"
                        "for y, s in d.groupby('year'):\n    print(y, round(float(s['value'].sum() / 1e9), 6), len(s))\n"),
}


def reproduce_py(name, region):
    P = next(p for p in CANDIDATES if p["name"] == name)
    label = P["label"][0].upper() + P["label"][1:]
    table = {"dc_construction": C30, "power_construction": C30, "dc_share": C30, "hosting_revenue": QSS}.get(name, CBP)
    head = PY_HEAD.format(name=name, region=region, table=table, label=label)
    if name in BODY:
        return head + BODY[name]
    st = region.rsplit("_", 1)[1]
    filt = "" if st == "US" else f"d = d[d['entity'] == 'census_cbp_518210:{st.lower()}']\n"
    if name == "hosting_pay":
        return head + filt + ("p = d[d['variable'].isin(['annual_payroll', 'employment'])].pivot_table(index=['year', 'entity'], columns='variable', values='value').dropna()\n"
                              "for y, s in p.groupby('year'):\n    print(y, round(float(s['annual_payroll'].sum() / s['employment'].sum() / 1000), 6), 1)\n")
    var = "employment" if name == "hosting_jobs" else "establishments"
    return head + filt + f"d = d[d['variable'] == {var!r}]\nfor y, s in d.groupby('year'):\n    print(y, round(float(s['value'].sum()), 6), 1)\n"


def reproduce_do(name, region):
    table = {"dc_construction": C30, "power_construction": C30, "dc_share": C30, "hosting_revenue": QSS}.get(name, CBP)
    lines = [f"* ERW findings hunt (chain 164): reproduce candidate {name} for {region} from the ERW's public table.",
             "* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.",
             "clear all", f'import delimited "{table}.csv", varnames(1) stringcols(_all) clear', "destring value, replace force", "drop if missing(value)",
             "generate int year = real(substr(ts_utc, 1, 4))"]
    if name in ("dc_construction", "power_construction"):
        ent = "census_c30:private:data_center" if name == "dc_construction" else "census_c30:private:electric"
        lines += [f'keep if entity == "{ent}" & variable == "value_put_in_place"', "collapse (sum) measure = value (count) n = value, by(year)",
                  "replace measure = measure / 1000000000"]
    elif name == "dc_share":
        lines += ['keep if (entity == "census_c30:private:data_center" | entity == "census_c30:private:nonresidential") & variable == "value_put_in_place"',
                  'generate str3 side = cond(entity == "census_c30:private:data_center", "dc", "all")', "keep year ts_utc side value",
                  "reshape wide value, i(ts_utc) j(side) string", "drop if missing(valuedc) | missing(valueall)",
                  "collapse (sum) dc = valuedc (sum) all = valueall (count) n = valuedc, by(year)", "generate double measure = 100 * dc / all"]
    elif name == "hosting_revenue":
        lines += ['keep if entity == "census_qss:518" & variable == "total_revenue"', "collapse (sum) measure = value (count) n = value, by(year)",
                  "replace measure = measure / 1000000000"]
    else:
        st = region.rsplit("_", 1)[1]
        lines += ([] if st == "US" else [f'keep if entity == "census_cbp_518210:{st.lower()}"'])
        if name == "hosting_pay":
            lines += ['generate double pay = value if variable == "annual_payroll"', 'generate double emp = value if variable == "employment"',
                      "collapse (sum) pay (sum) emp, by(year entity)", "drop if pay == 0 | emp == 0", "collapse (sum) pay (sum) emp, by(year)",
                      "generate double measure = pay / emp / 1000", "generate byte n = 1"]
        else:
            var = "employment" if name == "hosting_jobs" else "establishments"
            lines += [f'keep if variable == "{var}"', "collapse (sum) measure = value, by(year)", "generate byte n = 1"]
    lines += ["sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
LIMIT_C30 = "The Census Bureau's value put in place, nominal dollars, not seasonally adjusted; the latest months are preliminary and are revised."
LIMIT_CBP = ("County Business Patterns counts establishments by their main activity, so a data center run inside another firm's establishment is not in it; "
             "the Census Bureau adds noise to protect respondents, and NAICS 518210's definition widened with the 2022 codes.")
CANDIDATES = [
    C("dc_construction", FAMILY, dc_construction, "USD billion", 2, 11, 2.0, "BUILDING DATA CENTERS",
      "the value of private data center construction put in place over the year", lambda w: "the value of private data center construction put in place in the US",
      LIMIT_C30, reproduce("dc_construction"), consequence=3),
    C("dc_share", FAMILY, dc_share, "percent of private nonresidential construction", 2, 11, 1.0, "DATA CENTERS IN CONSTRUCTION",
      "data centers' share of the value of private nonresidential construction put in place over the year",
      lambda w: "data centers' share of US private nonresidential construction", LIMIT_C30, reproduce("dc_share"), consequence=3),
    C("power_construction", FAMILY, power_construction, "USD billion", 2, 11, 5.0, "BUILDING POWER",
      "the value of private electric power construction put in place over the year", lambda w: "the value of private electric power construction put in place in the US",
      LIMIT_C30 + " Electric power construction counts generation, transmission and distribution projects together.", reproduce("power_construction"), consequence=3),
    C("hosting_jobs", FAMILY, hosting_jobs, "employees", 0, 1, 5000.0, "JOBS IN DATA PROCESSING AND HOSTING",
      "mid-March employment in NAICS 518210 establishments", lambda w: f"the mid-March employment of data processing and hosting establishments in {w}",
      LIMIT_CBP, reproduce("hosting_jobs"), consequence=2),
    C("hosting_sites", FAMILY, hosting_sites, "establishments", 0, 1, 200.0, "DATA PROCESSING AND HOSTING SITES",
      "the number of NAICS 518210 establishments", lambda w: f"the number of data processing and hosting establishments in {w}",
      LIMIT_CBP, reproduce("hosting_sites"), consequence=2),
    C("hosting_pay", FAMILY, hosting_pay, "USD thousand a year", 1, 1, 5.0, "PAY IN DATA PROCESSING AND HOSTING",
      "annual payroll per mid-March employee in NAICS 518210", lambda w: f"the annual payroll per employee of data processing and hosting establishments in {w}",
      LIMIT_CBP + " Nominal dollars.", reproduce("hosting_pay"), consequence=1),
    C("hosting_revenue", FAMILY, hosting_revenue, "USD billion", 1, 4, 10.0, "WHAT DATA PROCESSING AND HOSTING EARN",
      "the revenue of NAICS 518 over the year, the Quarterly Services Survey", lambda w: "the revenue of US data processing and hosting firms (NAICS 518)",
      "The Quarterly Services Survey's estimate, nominal dollars, not seasonally adjusted; NAICS 518 covers far more than data centers.",
      reproduce("hosting_revenue"), consequence=2),
]
for _P in CANDIDATES:
    if _P["name"] in ("hosting_jobs", "hosting_sites", "hosting_pay"):
        _P["rank_region"] = generation._us_first
        _P["rank"] = lambda c: abs(c["change"])


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt, family datacenters (chain 164)")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--only", default=None)
    ap.add_argument("--replace", action="store_true", help="correct the open drafts of the same claims in place")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    cands = [P for P in CANDIDATES if not a.only or P["name"] == a.only]
    builder.run(FAMILY + "_datacenters", cands, a.in_dir, dry_run=not a.load, replace=a.replace)
    return 0


if __name__ == "__main__":
    sys.exit(main())
