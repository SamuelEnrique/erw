#!/usr/bin/env python3
"""The California Energy Commission's Total System Electric Generation: California's in-state generation by fuel, the
imports from the Northwest and the Southwest by fuel, and the state's total system power, a year (session 2109, chain
069: California's own account of its generation, beside EIA's).

Energy Research Warehouse (ERW) connector. One series table from the Commission's workbook "Total System Electric
Generation 2009 to <latest> with totals", linked from the Energy Almanac's download page:

    https://www.energy.ca.gov/media/7311   (the page; the workbook's address is read from it)

    cec_total_system_generation_annual   entity cec_tsp:<region>:<fuel> (region california, northwest, southwest, or
               total for the total system; fuel biomass, coal, geothermal, large_hydro, natural_gas, nuclear, oil,
               other, small_hydro, solar, unspecified, wind, and in the total block oil_other and unspecified_imports
               as the Commission combines them); variable in_state_generation (california), imports (northwest and
               southwest) or total_system_power (total); unit MWh (the Commission's GWh times 1,000); ts_utc 1 January;
               freq P1Y; geo US-CA; node the region and fuel as the workbook names them; x_region; x_fuel

The workbook's one sheet must hold a header row "Region", "Fuel Type" and the years, and blocks for California,
Northwest and Southwest, each with its total row, then Total Imports, the Total block by fuel and the Grand Total. Every
region's fuels must sum to its total row, the two import regions to Total Imports, each fuel of the Total block to the
three regions' (oil and other together), and the Total block to the Grand Total, within 1 GWh, or the run stops. The
total rows are checked and not kept. A cell the Commission writes as a dash or leaves blank has no row, and the header
counts them; a row of the Total block with no fuel and no figure (the workbook has one) is passed over. Nothing is
filled.

    python warehouse/connectors/cec_total_system.py [--offline] [--out-dir DIR]

Ceiling: two requests (the page and the workbook, saved in warehouse/raw/cec_total_system/ and reused offline; asked again unless --offline, since the page keeps its address). The
Commission's robots file disallows /core/, /profiles/, /search/, /admin/ and the user pages, not /media/ or
/sites/default/files/. License: may be public, noncommercial with credit (the Commission's Conditions of Use, read 245: its
materials are free for public use crediting the Commission; commercial or profit-making use is prohibited).
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback
import urllib.parse

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "cec_total_system"
SOURCE = "cec:total_system_electric_generation"
HOST = "www.energy.ca.gov"
PAGE = "https://www.energy.ca.gov/media/7311"
TABLE = "cec_total_system_generation_annual"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
X_COLS = ["x_region", "x_fuel"]
REGIONS = {"California": ("california", "in_state_generation"), "Northwest": ("northwest", "imports"), "Southwest": ("southwest", "imports"),
           "Total": ("total", "total_system_power")}
FUELS = {"biomass": "biomass", "coal": "coal", "geothermal": "geothermal", "largehydro": "large_hydro", "naturalgas": "natural_gas",
         "nuclear": "nuclear", "oil": "oil", "otherwasteheatpetroleumcoke": "other", "smallhydro": "small_hydro", "solar": "solar",
         "unspecified": "unspecified", "wind": "wind", "oilother": "oil_other", "unspecifiedimports": "unspecified_imports"}
TOTALS = {"californiatotal": "california", "northwesttotal": "northwest", "southwesttotal": "southwest", "totalimports": "imports",
          "grandtotal": "grand"}
TOL = 1.0  # GWh: the Commission rounds


def letters(s):
    return re.sub(r"[^a-z]", "", str(s).lower())


def workbook_url(page):
    hits = sorted(set(h for h in re.findall(r'href="([^"]+\.xlsx)"', page) if "total_system_electric_generation" in h.lower()))
    if len(hits) != 1:
        raise RuntimeError(f"the page links not one Total System Electric Generation workbook: {hits}")
    return urllib.parse.urljoin(PAGE, hits[0])


def cell(x, where, dashes):
    if isinstance(x, str):
        if x.strip() in ("-", ""):
            dashes.append(where + (" (blank)" if not x.strip() else ""))
            return None
        raise RuntimeError(f"{where}: not a number: {x!r}")
    if isinstance(x, bool) or pd.isna(x):
        raise RuntimeError(f"{where}: not a number: {x!r}")
    return float(x)


def parse(content, base):
    v = pd.read_excel(io.BytesIO(content), sheet_name=0, header=None, dtype=object, keep_default_na=False)
    h = [i for i in range(min(len(v), 10)) if str(v.iat[i, 0]).strip() == "Region" and str(v.iat[i, 1]).strip() == "Fuel Type"]
    if len(h) != 1:
        raise RuntimeError("no single header row 'Region', 'Fuel Type'")
    h = h[0]
    years = {j: int(v.iat[h, j]) for j in range(2, v.shape[1]) if re.fullmatch(r"\d{4}", str(v.iat[h, j]).strip())}
    if not years or sorted(years.values()) != list(range(min(years.values()), max(years.values()) + 1)):
        raise RuntimeError(f"the years are not a run of years: {sorted(years.values())}")
    out, dashes, totals, seen = [], [], {}, set()
    for i in range(h + 1, len(v)):
        region, fuel = str(v.iat[i, 0]).strip(), str(v.iat[i, 1]).strip()
        if not region and not fuel:
            continue
        if (region or fuel).startswith("All figures are gigawatt-hours"):
            continue  # the workbook's note, in its second column
        key = letters(region or fuel)
        if not region and key in TOTALS or (region and letters(region) in TOTALS):
            name = TOTALS[letters(region) if region and letters(region) in TOTALS else key]
            totals[name] = {fy: cell(v.iat[i, j], f"{name} total {fy}", dashes) for j, fy in years.items()}
            continue
        if region == "Total" and not fuel and not any(str(v.iat[i, j]).strip() for j in years):
            continue  # the Total block's empty row
        if region not in REGIONS:
            raise RuntimeError(f"row {i}: a region not in the map: {region!r} {fuel!r}")
        if letters(fuel) not in FUELS:
            raise RuntimeError(f"row {i}: a fuel not in the map: {fuel!r}")
        rslug, var = REGIONS[region]
        fslug = FUELS[letters(fuel)]
        if (rslug, fslug) in seen:
            raise RuntimeError(f"{region} {fuel} given twice")
        seen.add((rslug, fslug))
        for j, fy in years.items():
            x = cell(v.iat[i, j], f"{region} {fuel} {fy}", dashes)
            if x is None:
                continue
            out.append(dict(base, entity=f"cec_tsp:{rslug}:{fslug}", variable=var, ts_utc=f"{fy}-01-01T00:00:00Z", value=round(x * 1000.0, 3),
                            unit="MWh", freq="P1Y", geo="US-CA", market="", node=f"{region}: {fuel}", x_region=rslug, x_fuel=fslug))
    missing = sorted(set(TOTALS.values()) - set(totals))
    if missing:
        raise RuntimeError(f"no total row for {missing}")
    return out, totals, sorted(years.values()), dashes


def check(rows, totals, years):
    s = pd.DataFrame(rows)
    gwh = s.assign(gwh=s.value / 1000.0).pivot_table(index=["x_region", "x_fuel"], columns=s.ts_utc.str[:4].astype(int), values="gwh", aggfunc="sum")
    for fy in years:
        col = gwh[fy] if fy in gwh.columns else pd.Series(dtype=float)
        for r in ("california", "northwest", "southwest"):
            t = totals[r][fy]
            got = col.xs(r, level=0).sum() if r in col.index.get_level_values(0) else 0.0
            if t is not None and abs(got - t) > TOL:
                raise RuntimeError(f"{r} {fy}: the fuels sum to {got:.3f} GWh, the total row is {t}")
        imp = totals["imports"][fy]
        if imp is not None and abs(totals["northwest"][fy] + totals["southwest"][fy] - imp) > TOL:
            raise RuntimeError(f"{fy}: Northwest and Southwest sum to {totals['northwest'][fy] + totals['southwest'][fy]}, Total Imports is {imp}")
        tot = col.xs("total", level=0)
        g = totals["grand"][fy]
        if abs(tot.sum() - g) > TOL:
            raise RuntimeError(f"{fy}: the Total block sums to {tot.sum():.3f} GWh, the Grand Total is {g}")
        regions = col.drop("total", level=0).groupby(level=1).sum()
        for fuel, t in tot.items():
            want = regions.get("oil", 0) + regions.get("other", 0) if fuel == "oil_other" else (
                regions.get("unspecified", 0) if fuel == "unspecified_imports" else regions.get(fuel, 0))
            if abs(want - t) > TOL:
                raise RuntimeError(f"{fy} {fuel}: the regions sum to {want:.3f} GWh, the Total block gives {t}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="The California Energy Commission's Total System Electric Generation")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        if ip.paused(CONNECTOR) or ip.paused_host(HOST):
            raise RuntimeError(f"{HOST} is paused (warehouse/metadata/paused_sources.csv): no request made")
        page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120, pause=1)
        url = workbook_url(page.decode("utf-8", errors="replace"))
        log(f"  workbook: {url}")
        content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120, pause=1)
        base = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        rows, totals, years, dashes = parse(content, base)
        check(rows, totals, years)
        s = pd.DataFrame(rows)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("an (entity, variable, ts_utc) given twice")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        head = [
            "Energy Research Warehouse (ERW): California Energy Commission, Total System Electric Generation, California's in-state generation and "
            f"its imports from the Northwest and the Southwest by fuel, and the total system power, {years[0]} to {years[-1]} (session 2109)",
            "Shape: series (docs/datastandard.md v0). entity cec_tsp:<california|northwest|southwest|total>:<fuel>; variable in_state_generation, "
            "imports or total_system_power; unit MWh (the Commission's GWh times 1,000); freq P1Y; ts_utc 1 January; geo US-CA; node the region and "
            "fuel as named; x_region, x_fuel. In the total block the Commission combines oil with other (oil_other) and names unspecified as "
            "unspecified_imports.",
            "Checked as read: each region's fuels sum to its total, the import regions to Total Imports, each fuel of the total block to the three "
            "regions' and the block to the Grand Total, within 1 GWh (the Commission rounds); the total rows are not kept. "
            f"Cells written as a dash or left blank have no row: {len(dashes)} ({'; '.join(dashes) or 'none'}). Nothing is filled. Imports are the "
            "Commission's estimates of the energy delivered to California, by the fuel of the generator; unspecified imports are power whose "
            "source is not traced.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/cec_total_system.py; the workbook retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} California Energy Commission, Energy Almanac, Total System Electric Generation, {PAGE}",
            f"  access: {url}",
            "License: may be public, noncommercial with credit (the Commission's Conditions of Use: its materials are free for public use "
            "crediting the Commission; commercial or profit-making use is prohibited; see license_verdicts.csv). Cite the California Energy "
            "Commission.",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s)} rows, {s.entity.nunique()} series, {years[0]} to {years[-1]}; dashes {len(dashes)}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="California Energy Commission (CEC)",
                                    report="Total System Electric Generation (Energy Almanac), the workbook of all years with totals",
                                    report_url=PAGE, document_list=PAGE, license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
