#!/usr/bin/env python3
"""EIA's buildings surveys: the Commercial Buildings Energy Consumption Survey (CBECS, 2018) and the Residential Energy
Consumption Survey (RECS, 2020), their consumption and expenditure tables by building or household characteristic
(session 2017, chain 057: buildings' energy, which the ERW held only as EIA's commercial sector a month).

Energy Research Warehouse (ERW) connector. Two series tables, each a survey's crosstabulations as EIA prints them:

    eia_cbecs_commercial_buildings   CBECS 2018, Tables C1 (consumption by major fuel), C2 (expenditures by major fuel)
                                     and E1 (major fuels' consumption by end use)
    eia_recs_households              RECS 2020, Tables CE4.1 (site consumption by fuel and end use) and CE4.11
                                     (expenditures by fuel and end use)

    entity cbecs:<heading>_<category> or recs:<heading>_<category> (each slugged, as the table prints them, except a
    footnote letter two of the survey's tables print differently, which is set aside so the category joins across them:
    "Climate zonec" and "Climate Zonea" are cbecs:climate_zone_..., session 2023; cbecs:all and recs:all for all
    buildings and all homes); variables named for the table's column (below); ts_utc 1 January of
    the survey year; freq P1Y; geo US (every figure is national or a part of the nation); node the category as printed;
    x_heading the heading it sits under (Principal building activity, Census region and division, Housing unit type,
    ...); x_level its indent (0 a category, 1 a part of the category above it, 2 a part of that), so a heading's level-0
    rows add up and a level-1 row is inside its x_parent; x_parent the category it is a part of; x_table the table

The tables' units are converted to the ERW's: trillion Btu is TBtu; million or billion dollars, and thousand or million
buildings and housing units, are multiplied out to USD and count. A cell EIA writes as a code has no row, and the codes
are counted in each table's header: "Q" withheld (relative standard error of 50 percent or more, or fewer than 20
cases), "N" no cases in the sample, "*" or "(*)" less than 0.5 of the unit, and "NA" or "W" if a table writes them.
Nothing is filled. Each column's header (the rows above the table's All buildings or All homes row, which must be in it,
and where its figures begin) must read as below, and a category given twice under one heading, a row with a figure
before any heading, or text where a figure belongs stops the run.

    python warehouse/connectors/eia_buildings.py [--offline] [--out-dir DIR]

Ceiling: five requests (the tables are saved in warehouse/raw/eia_buildings/ and reused). EIA's robots file does not
disallow /consumption/. License: public (EIA, read 1). The latest surveys with consumption: CBECS 2018 (2024's is being
fielded) and RECS 2020 (2024's has published preliminary housing characteristics only).
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import openpyxl
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "eia_buildings"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
X_COLS = ["x_heading", "x_level", "x_parent", "x_table"]
CODES = {"Q", "N", "*", "(*)", "NA", "W"}
CB = "https://www.eia.gov/consumption/commercial/data/2018/"
RE = "https://www.eia.gov/consumption/residential/data/2020/"
ELEC_USES = ["total", "space_heating", "water_heating", "air_conditioning", "refrigerators", "other"]
FUEL_USES = ["total", "space_heating", "water_heating", "other"]


def recs_cols(prefix):
    """CE4.1 and CE4.11: housing units, the total, then electricity's six columns and three fuels' four each."""
    cols = {1: ("housing_units", "Total U.S.")}
    cols[2] = (f"{prefix}_total", "Total")
    j = 3
    for fuel, uses in (("electricity", ELEC_USES), ("natural_gas", FUEL_USES), ("propane", FUEL_USES), ("fuel_oil_kerosene", FUEL_USES)):
        for u in uses:
            cols[j] = (f"{prefix}_{fuel}_{u}", {"total": "Total", "space_heating": "Space heating", "water_heating": "Water heating",
                                                "air_conditioning": "Air condi", "refrigerators": "Refrig", "other": "Other"}[u])
            j += 1
    return cols


# table -> (survey, file, sheet, {column: (variable, text its header must hold)}, {variable prefix: (factor, unit)}, the unit's
# words in the table's top rows, a pattern)
TABLES = {
    "C1": ("cbecs", CB + "ce/xls/c1.xlsx", "data", {
        1: ("buildings", "Number of buildings"), 3: ("consumption_sum_major_fuels", "major"), 4: ("consumption_electricity_primary", "Primary"),
        5: ("consumption_electricity_site", "Site"), 6: ("consumption_natural_gas", "Natural"), 7: ("consumption_fuel_oil", "Fuel"),
        8: ("consumption_district_heat", "District")}, {"buildings": (1000.0, "count"), "consumption": (1.0, "TBtu")}, r"trillion (btu|british thermal units)"),
    "C2": ("cbecs", CB + "ce/xls/c2.xlsx", "data", {
        3: ("expenditure_sum_major_fuels", "major"), 4: ("expenditure_electricity", "Electricity"), 5: ("expenditure_natural_gas", "Natural"),
        6: ("expenditure_fuel_oil", "Fuel"), 7: ("expenditure_district_heat", "District")}, {"expenditure": (1e6, "USD")}, r"million dollars"),
    "E1": ("cbecs", CB + "ce/xls/e1.xlsx", "data", {
        1: ("enduse_total", "Total"), 2: ("enduse_space_heating", "Space"), 3: ("enduse_cooling", "Cooling"), 4: ("enduse_ventilation", "Venti"),
        5: ("enduse_water_heating", "Water"), 6: ("enduse_lighting", "Lighting"), 7: ("enduse_cooking", "Cooking"), 8: ("enduse_refrigeration", "Refrig"),
        9: ("enduse_office_equipment", "Office"), 10: ("enduse_computing", "puting"), 11: ("enduse_other", "Other")}, {"enduse": (1.0, "TBtu")},
        r"trillion (btu|british thermal units)"),
    "CE4.1": ("recs", RE + "c&e/xls/ce4.1.xlsx", "Btu", recs_cols("consumption"), {"housing": (1e6, "count"), "consumption": (1.0, "TBtu")},
              r"trillion (btu|british thermal units)"),
    "CE4.11": ("recs", RE + "c&e/xls/ce4.11.xlsx", "dollars", recs_cols("expenditure"), {"housing": (1e6, "count"), "expenditure": (1e9, "USD")},
               r"billion dollars"),
}
SURVEYS = {
    "cbecs": dict(table="eia_cbecs_commercial_buildings", year=2018, all="All buildings", source="eia:cbecs_2018", page=CB,
                  name="2018 Commercial Buildings Energy Consumption Survey (CBECS)", units={"buildings": "thousand"}),
    "recs": dict(table="eia_recs_households", year=2020, all="All homes", source="eia:recs_2020", page=RE,
                 name="2020 Residential Energy Consumption Survey (RECS)", units={"housing_units": "million"}),
}


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", str(s).lower()).strip("_")


def flat(s):
    return re.sub(r"\s+", " ", str(s).replace("-\n", "").replace("\n", " ")).strip()


def parse(content, name, base, counts):
    """The rows of one table: a heading is a bold row without figures; a category's indent is its level."""
    survey, url, sheet, cols, units, unit_text = TABLES[name]
    sv = SURVEYS[survey]
    ws = openpyxl.load_workbook(io.BytesIO(content), data_only=True)[sheet]
    rows = [[c for c in r] for r in ws.iter_rows()]
    title = " ".join(flat(r[0].value) for r in rows[:3] if r and r[0].value)
    want = f"Table {name}"
    top = " ".join(flat(c.value) for r in rows[:6] for c in r if c.value).lower()
    if not re.search(re.escape(want) + r"\b", title) or not re.search(unit_text, top):
        raise RuntimeError(f"{name}: the title or the unit is not as read: {title[:140]!r}")
    first = next((i for i, r in enumerate(rows) if r[0].value and flat(r[0].value) == sv["all"]), None)
    if first is None:
        raise RuntimeError(f"{name}: no row {sv['all']!r}")
    for j, (var, text) in cols.items():
        head = " ".join(flat(rows[i][j].value) for i in range(2, first) if j < len(rows[i]) and rows[i][j].value)
        if text.lower() not in head.lower():
            raise RuntimeError(f"{name}: column {j} ({var}) should read {text!r}; it reads {head!r}")
    out, heading, parents, seen = [], None, {}, set()
    for i in range(first, len(rows)):
        r = rows[i]
        label = flat(r[0].value) if r[0].value is not None else ""
        if not label or label.startswith(("Data source", "Note", "Source")):
            if label.startswith(("Data source", "Note", "Source")):
                break
            continue
        cells = {j: (r[j].value if j < len(r) else None) for j in cols}
        filled = {j: v for j, v in cells.items() if v is not None and str(v).strip() != ""}
        if not filled:
            if not r[0].font.b:
                raise RuntimeError(f"{name} row {i + 1}: {label!r} has no figure and is not a bold heading")
            heading, parents = label, {}
            continue
        if i == first:
            h, level, parent, ent = "", 0, "", f"{survey}:all"
        else:
            if heading is None:
                raise RuntimeError(f"{name} row {i + 1}: {label!r} before any heading")
            level = int(r[0].alignment.indent or 0)
            parents = {k: v for k, v in parents.items() if k < level}
            parents[level] = label
            path = [parents.get(k) for k in range(level + 1)]
            if None in path:
                raise RuntimeError(f"{name} row {i + 1}: {label!r} is indented {level} under no category")
            parent = path[-2] if level else ""
            # a part is named with the categories it sits in (RECS prints Single-family under Owned and under Rented)
            h, ent = heading, f"{survey}:{slug(heading)}_" + "_".join(slug(x) for x in path)
        if (ent, name) in seen:
            raise RuntimeError(f"{name}: {label!r} given twice under {heading!r}")
        seen.add((ent, name))
        for j, v in filled.items():
            var = cols[j][0]
            factor, unit = units[var.split("_")[0]]
            if isinstance(v, str):
                if v.strip() in CODES:
                    counts[v.strip()] = counts.get(v.strip(), 0) + 1
                    continue
                raise RuntimeError(f"{name} {label!r} {var}: not a number: {v!r}")
            out.append(dict(base, entity=ent, variable=var, ts_utc=f"{sv['year']}-01-01T00:00:00Z", value=round(float(v) * factor, 6), unit=unit,
                            freq="P1Y", geo="US", market="", node=label, x_heading=h, x_level=level, x_parent=parent, x_table=name,
                            _path=tuple(path) if i != first else ()))
    if not out:
        raise RuntimeError(f"{name}: no row")
    return out


def footnotes(rows):
    """Session 2023: {printed text: text without its footnote letter} for the headings and labels two of a survey's tables
    print with different footnote letters (CBECS's "Climate zonec" in C1, "Climate Zonea" in C2 and E1; "Other sourcesd"
    and "Other sourcesb"). Only a text ending in a lowercase letter, matched case-blind on everything but that letter by a
    text of another table, is changed, so a category joins across the tables; any other text is kept as printed."""
    where = {}
    for r in rows:
        for t in (r["x_heading"],) + tuple(r["_path"]):
            if t:
                where.setdefault(t, set()).add(r["x_table"])
    out, by_base = {}, {}
    for t in where:
        if t[-1].islower():
            by_base.setdefault(t[:-1].lower(), []).append(t)
    for base, texts in by_base.items():
        tables = [where[t] for t in texts]
        if len(texts) > 1 and any(a.isdisjoint(b) for k, a in enumerate(tables) for b in tables[k + 1:]):
            for t in texts:
                out[t] = texts[0][:-1].rstrip()
    return out


def rename(rows, survey):
    """Each row's entity and heading from the texts without the letters footnotes() found; node stays as printed."""
    canon = footnotes(rows)
    for r in rows:
        path = r.pop("_path")
        r["x_heading"] = canon.get(r["x_heading"], r["x_heading"])
        r["x_parent"] = canon.get(r["x_parent"], r["x_parent"])
        if path:
            r["entity"] = f"{survey}:{slug(r['x_heading'])}_" + "_".join(slug(canon.get(x, x)) for x in path)
    return rows, canon


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's CBECS 2018 and RECS 2020 consumption and expenditure tables")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--out-dir", help="a trial: the tables under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results, sources = [], []
    for survey, sv in SURVEYS.items():
        table = sv["table"]
        try:
            # session 2066: the pause list first (CLAUDE.md), as boem_ogor.py asks it
            if ip.paused(CONNECTOR) or ip.paused_host("www.eia.gov"):
                raise RuntimeError("www.eia.gov is paused (warehouse/metadata/paused_sources.csv): no request made")
            rows, latest, counts, urls = [], "", {}, []
            for name, (s_, url, _, _, _, _) in TABLES.items():
                if s_ != survey:
                    continue
                content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=120, pause=1)
                base = dict(source=sv["source"], source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
                got = parse(content, name, base, counts)
                log(f"  {name}: {len(got)} rows")
                rows += got
                urls.append(url)
                latest = max(latest, base["retrieved_at"])
            rows, canon = rename(rows, survey)
            if canon:
                log(f"  footnote letters set aside for the entity ids: {sorted(canon.items())}")
            s = pd.DataFrame(rows)
            if s.duplicated(["entity", "variable", "x_table"]).any():
                raise RuntimeError("a footnote letter set aside made two categories of one table one")
            # a column two tables share (RECS's housing units) must agree, and is kept once
            dup = s.duplicated(["entity", "variable", "ts_utc"], keep=False)
            if dup.any():
                d = s[dup].groupby(["entity", "variable"]).value.agg(["min", "max"])
                if ((d["max"] - d["min"]).abs() > 1e-6 * d["max"].abs().clip(lower=1)).any():
                    raise RuntimeError(f"a figure two tables share differs: {d[(d['max'] - d['min']).abs() > 0].head(3).to_dict('index')}")
                s = s.drop_duplicates(["entity", "variable", "ts_utc"], keep="first")
            cols = ip.SERIES_COLS + X_COLS
            s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
            coded = ", ".join(f"{k} {n}" for k, n in sorted(counts.items())) or "none"
            head = [
                f"Energy Research Warehouse (ERW): EIA, {sv['name']}, consumption and expenditure by building or household characteristic, as "
                f"EIA's tables {', '.join(n for n, t in TABLES.items() if t[0] == survey)} print them (session 2017)",
                "Shape: series (docs/datastandard.md v0). entity <survey>:<heading>_<category>, or <survey>:all; variables named for the table's "
                "columns; units TBtu, USD and count (EIA's trillion Btu; its million or billion dollars and thousand or million buildings or housing "
                "units multiplied out); freq P1Y; ts_utc 1 January of the survey year; geo US; node the category as printed; x_heading its heading (a footnote letter two tables print differently set aside, as in the entity); x_level its "
                "indent (a level-1 row is a part of its x_parent: add level-0 rows only); x_table the table.",
                f"{s.entity.nunique()} categories. Cells EIA writes as codes have no row: {coded} (Q withheld; N no cases; * or (*) less than 0.5). "
                "Nothing is filled. A survey estimate: each figure has a relative standard error, in EIA's rse sheets, not taken.",
                f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_buildings.py; the latest file retrieved {latest}",
                f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
                f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
                f"Source: {sv['source']} U.S. Energy Information Administration, {sv['name']}, {sv['page']}",
                f"  access: {', '.join(urls)}",
                "License: public (EIA: U.S. government publications are in the public domain).",
            ]
            ip.write_snapshot(s, table, head, log, cols)
            results.append(dict(table=table, market="all", status="ok", detail=f"{len(s)} rows"))
            sources.append(dict(source=sv["source"], publisher="U.S. Energy Information Administration (EIA)",
                                report=f"{sv['name']}: consumption and expenditures, Tables {', '.join(n for n, t in TABLES.items() if t[0] == survey)}",
                                report_url=sv["page"], document_list=sv["page"] + "index.php?view=consumption", license="public", tables=[table]))
            print(f"{table}: {len(s)} rows, {s.entity.nunique()} categories; codes {coded}")
        except Exception:
            tb = ip.redact(traceback.format_exc())
            log(f"{table} FAILED, no output file written:\n{tb}")
            print(f"{table} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
            results.append(dict(table=table, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if sources:
            ip.update_sources(sources)
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
