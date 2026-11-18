#!/usr/bin/env python3
"""Each county of the lower 48 to its balancing authority and its EIA region (session 7802, chain 401 part C, table 5).

Energy Research Warehouse (ERW) derived table, an entities table,

    warehouse/output/eia_county_region.csv

from tables the warehouse holds (no request is made):
  utility_service_territories   EIA-861's Service_Territory sheets: which utility serves which county (by name), 2025
  eia861_utility_sales and      EIA-861's sales file and its delivery-only file: each utility's balancing authority in each
  eia861_delivery_only          state (x_ba_code) and its
                                total retail customers, data year 2025
  census_county_population      the Census Bureau's county codes and names (vintage 2025 and the 2020 intercensal files)
  the newest EIA-930 six-month BALANCE file saved by warehouse/connectors/eia930_region_hourly.py: each balancing
                                authority's EIA region ("Region")

Rule (docs/methods/county_population_and_regions.md). A county's balancing authorities are those of every utility EIA-861
lists as serving it (the utility's x_ba_code in that state, data year 2025). One balancing authority: that one. More than
one: the county is marked shared (x_shared Y), every one is listed (x_bas, with their utilities' customers), and the
primary is the one whose serving utilities have the most total retail customers in the state (parts A, bundled, and C,
delivery, of EIA-861's sales; the energy-only and other parts when a utility files neither), ties broken by the code.
The other rule that was open, the balancing authority with the most serving utilities in the county, is in x_ba_by_count
for a reader who prefers it (Decisions made without Samuel, session 7802). The region is the primary balancing
authority's EIA-930 region; x_regions lists every listed balancing authority's region. A county EIA-861 lists no utility
for, or whose utilities name no balancing authority, is written with x_basis saying so and no balancing authority.

County names: EIA-861 writes a county by its name ("Anderson", "Baltimore City"); matched to the Bureau's names
("Anderson County", "Baltimore city") after both are lowercased, "county", "parish", "borough", "census area" and
"municipality" dropped, "saint" read as "st", and points, apostrophes, hyphens and spaces removed. A territory row whose
name matches no county of its state is counted in the header and the run log, never guessed.

    python warehouse/derived/eia_county_region.py [--out-dir DIR]
"""

import argparse
import datetime as dt
import glob
import os
import re
import sys
import traceback
import unicodedata

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

NAME = "eia_county_region"
SOURCE = "erw:eia_county_region"
METHOD = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/county_population_and_regions.md"
LOWER48_EXCLUDED = {"AK", "HI"}
FIPS_ABBR = {"01": "AL", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT", "10": "DE", "11": "DC", "12": "FL", "13": "GA",
             "16": "ID", "17": "IL", "18": "IN", "19": "IA", "20": "KS", "21": "KY", "22": "LA", "23": "ME", "24": "MD", "25": "MA",
             "26": "MI", "27": "MN", "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH", "34": "NJ", "35": "NM",
             "36": "NY", "37": "NC", "38": "ND", "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD",
             "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA", "54": "WV", "55": "WI", "56": "WY"}
COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator", "source",
        "source_url", "retrieved_at", "vintage", "x_state", "x_fips", "x_ba_primary", "x_region", "x_shared", "x_bas",
        "x_regions", "x_ba_by_count", "x_utilities", "x_basis"]


def key(name):
    # accents read as their letters (the Bureau's "Doña Ana", EIA-861's "Dona Ana")
    s = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode().lower().strip()
    s = re.sub(r"\b(county|parish|borough|census area|municipality|city and borough)\b", "", s)
    s = re.sub(r"\bsaint\b", "st", s)
    return re.sub(r"[.'\-\s]", "", s)


def read_table(name):
    path = os.path.join(ip.OUT_DIR if os.path.exists(os.path.join(ip.OUT_DIR, name + ".csv")) else READ_DIR, name + ".csv")
    n = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            n += 1
    return pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False), path


READ_DIR = ip.OUT_DIR  # before any --out-dir: a trial reads this checkout's tables, read only


def ba_regions():
    files = sorted(glob.glob(os.path.join(ip.RAW_DIR if os.path.isdir(os.path.join(ip.RAW_DIR, "eia930_region_hourly")) else RAW_READ,
                                          "eia930_region_hourly", "*", "*EIA930_BALANCE_*.csv")),
                   key=lambda p: (re.search(r"BALANCE_(\d{4})_(Jan_Jun|Jul_Dec)", p).groups(), p))
    newest = files[-1]
    d = pd.read_csv(newest, usecols=["Balancing Authority", "Region"], dtype=str).drop_duplicates()
    return dict(zip(d["Balancing Authority"], d["Region"])), os.path.basename(newest)


RAW_READ = ip.RAW_DIR


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW county to balancing authority and EIA region (session 7802)")
    ap.add_argument("--out-dir")
    args = ap.parse_args(argv)
    if args.out_dir:
        ip.set_out_dir(args.out_dir)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    results = []
    try:
        terr, terr_path = read_table("utility_service_territories")
        # the wires utilities of the competitive areas (Texas's in ERCOT, among others) file in EIA-861's delivery-only file
        sales = pd.concat([read_table("eia861_utility_sales")[0], read_table("eia861_delivery_only")[0]], ignore_index=True)
        pop, _ = read_table("census_county_population")
        region_of, balance_file = ba_regions()
        year = sales["ts_utc"].max()
        s = sales[(sales["ts_utc"] == year) & (sales["variable"] == "total_customers")].copy()
        s["customers"] = pd.to_numeric(s["value"], errors="coerce").fillna(0)
        s["wires"] = s["x_part"].isin(["A", "C"])
        # one row per utility, state and balancing authority: customers of the wires parts where the utility files one
        g = s.groupby(["x_utility_number", "x_state", "x_ba_code"]).apply(
            lambda x: x.loc[x["wires"], "customers"].sum() if x["wires"].any() else x["customers"].sum(), include_groups=False)
        uba = g.rename("customers").reset_index()
        uba = uba[uba["x_ba_code"].str.strip() != ""]
        # the lower 48 and the District of Columbia: Alaska, Hawaii and the territories (PR, GU, VI, AS, MP) are left out
        terr = terr[terr["x_state"].isin(set(FIPS_ABBR.values()))].copy()
        terr["k"] = terr["x_county"].map(key)
        # the Bureau's counties of the lower 48: every code either product prints, with its newest name
        pop["fips"] = pop["entity_id" if "entity_id" in pop else "entity"].str[-5:]
        pop = pop[pop["fips"].str[:2].isin(FIPS_ABBR)]
        pop["state"] = pop["fips"].str[:2].map(FIPS_ABBR)
        names = pop.sort_values("ts_utc").groupby("fips").agg(name=("node", "last"), state=("state", "first")).reset_index()
        names["k"] = names["name"].map(key)
        clash = names.duplicated(["state", "k"], keep=False)
        if clash.any():
            log(f"  county names that read alike after the rule (kept apart by code; a territory row naming them is not matched): "
                f"{names[clash][['fips', 'name']].values.tolist()}")
        lookup = names[~clash].set_index(["state", "k"])["fips"]
        terr["fips"] = [lookup.get((st, k)) for st, k in zip(terr["x_state"], terr["k"])]
        unmatched = terr[terr["fips"].isna()]
        log(f"  territory rows: {len(terr):,}; matched to a county {terr['fips'].notna().sum():,}; unmatched {len(unmatched):,}: "
            f"{sorted(set((unmatched['x_state'] + ':' + unmatched['x_county']).tolist()))[:200]}")
        m = terr.dropna(subset=["fips"]).merge(uba, on=["x_utility_number", "x_state"], how="left")
        rows = []
        for fips, grp in names.groupby("fips"):
            st, nm = grp["state"].iloc[0], grp["name"].iloc[0]
            mine = m[m["fips"] == fips]
            utils = sorted(set(mine["x_utility_number"]))
            withba = mine.dropna(subset=["x_ba_code"])
            if not len(mine):
                basis, bas, primary, bycount = "no utility listed by EIA-861 for this county", [], "", ""
            elif not len(withba):
                basis, bas, primary, bycount = "its utilities name no balancing authority in EIA-861's sales file", [], "", ""
            else:
                cust = withba.groupby("x_ba_code")["customers"].sum().sort_values(ascending=False)
                cnt = withba.groupby("x_ba_code")["x_utility_number"].nunique()
                order = sorted(cust.index, key=lambda b: (-cust[b], b))
                primary = order[0]
                bycount = sorted(cnt.index, key=lambda b: (-cnt[b], -cust[b], b))[0]
                bas = [f"{b} ({int(cust[b]):,} customers, {cnt[b]} utilities)" for b in order]
                basis = "one balancing authority" if len(order) == 1 else "shared: primary by the serving utilities' customers in the state"
            regions = sorted({region_of.get(b.split(" ")[0], "") for b in bas} - {""})
            rows.append(dict(entity_id=f"census:county:{fips}", entity_type="county", name=nm, geo=f"US-{st}", source=SOURCE,
                             source_url=METHOD, retrieved_at=ip.utc_iso(pd.Timestamp.now(tz="UTC")), vintage=f"EIA-861 {year[:4]}",
                             x_state=st, x_fips=fips, x_ba_primary=primary, x_region=region_of.get(primary, ""),
                             x_shared="Y" if len(bas) > 1 else "N", x_bas="; ".join(bas), x_regions=";".join(regions),
                             x_ba_by_count=bycount, x_utilities=";".join(utils), x_basis=basis))
        out = pd.DataFrame(rows)
        for c in COLS:
            if c not in out:
                out[c] = ""
        out = out[COLS]
        n_shared, n_none = int((out["x_shared"] == "Y").sum()), int((out["x_ba_primary"] == "").sum())
        header = [
            "Energy Research Warehouse (ERW): each county of the lower 48 to its balancing authority and its EIA region (session 7802)",
            "Shape: entities (docs/datastandard.md v0). entity_id census:county:<FIPS>; x_ba_primary and x_region (EIA-930 code and "
            "region); x_shared Y when EIA-861 lists utilities of more than one balancing authority in the county, x_bas every one "
            "with its utilities' customers in the state, primary the most customers (x_ba_by_count: the most utilities). Method: "
            "docs/methods/county_population_and_regions.md.",
            f"Retrieved: {run_id} (UTC) by warehouse/derived/eia_county_region.py",
            f"Run log: warehouse/output/logs/{NAME}_{run_id}.log",
            f"Source: {SOURCE} the ERW's county to balancing authority rule, {METHOD}",
            "  read from: eia:eia861_territory EIA-861 Service Territory (utility_service_territories), "
            "https://www.eia.gov/electricity/data/eia861/",
            f"  read from: eia:eia861 EIA-861 sales to ultimate customers (eia861_utility_sales, data year {year[:4]}, x_ba_code and "
            "total_customers), https://www.eia.gov/electricity/data/eia861/",
            "  read from: census_county_population (the Census Bureau's county codes and names)",
            f"  read from: {balance_file} (each balancing authority's EIA-930 region), https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/",
            f"Counties: {len(out):,}; shared {n_shared:,}; with no balancing authority {n_none:,}; territory rows whose county name "
            f"matched no county of its state: {len(unmatched):,} (listed in the run log).",
            "License: public (derived by the ERW from U.S. Energy Information Administration and U.S. Census Bureau data).",
        ]
        ip.write_snapshot(out, NAME, header, log, COLS)
        ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (from EIA-861, EIA-930 and Census Bureau data)",
                                report="County to balancing authority and EIA region", report_url=METHOD, document_list="",
                                license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(out)} counties, {n_shared} shared, {n_none} with none"))
        print(f"{NAME}: {len(out):,} counties, {n_shared:,} shared, {n_none:,} with no balancing authority, {len(unmatched):,} territory rows unmatched")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"{NAME} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    ip.write_status(NAME, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
