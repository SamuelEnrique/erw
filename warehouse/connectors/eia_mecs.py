#!/usr/bin/env python3
"""EIA's Manufacturing Energy Consumption Survey (MECS): manufacturing's fuel consumption by industry (NAICS), census
region and energy source, and its electricity's purchases, transfers, onsite generation, sales and net demand (session
2016, chain 057: industry's energy, which the ERW held only as EIA's whole industrial sector a month).

Energy Research Warehouse (ERW) connector. One series table from three of the 2022 survey's tables:

    https://www.eia.gov/consumption/manufacturing/data/2022/xls/Table3_2.xlsx    fuel consumption (trillion Btu)
    https://www.eia.gov/consumption/manufacturing/data/2022/xls/Table11_1.xlsx   electricity: components of net demand
    https://www.eia.gov/consumption/manufacturing/data/2022/xls/Table11_3.xlsx   electricity: components of onsite generation

    eia_mecs_manufacturing   entity mecs:<region>_<naics> (region us, northeast, midwest, south or west; naics the table's code, or
               total for all manufacturing, NAICS 31 to 33); variables fuel_<source> (TBtu: total, net_electricity,
               residual_fuel_oil, distillate_fuel_oil, natural_gas, hgl, coal, coke_and_breeze, hydrogen, other) from
               Table 3.2; elec_purchases, elec_transfers_in, elec_onsite_generation, elec_sales_transfers_offsite,
               elec_net_demand from Table 11.1 and gen_cogeneration, gen_renewable, gen_other from Table 11.3 (MWh, the
               tables' million kWh times 1,000); ts_utc 1 January of the survey year; freq P1Y; geo US for the nation,
               empty for a census region; node the industry as the table names it; x_naics the code; x_region the
               region as the table names it; x_table the table; x_mark a letter EIA prints beside the figure (h,
               "Revised data")

Each table's sheet must hold a header row whose first cell is "codea" (EIA's "NAICS code" with its footnote letter), the
columns read below, and region blocks headed "Total United States" and "<Region> Census Region". A cell EIA writes as a
code has no row, and the codes are counted in the header: "*" an estimate less than 0.5, "D" withheld to avoid disclosing
an establishment's data, "Q" withheld because its relative standard error is above 50 percent, "NA" not available.
Nothing is filled. Hydrogen is shown at the national level only: in a region it is inside Other (Table 3.2's note f).
Table 11.3's total onsite generation must equal Table 11.1's wherever both are figures, or the run stops. A column not
found, an industry given twice in a region, or a figure that is not a number stops the run.

    python warehouse/connectors/eia_mecs.py [--offline] [--out-dir DIR]

Ceiling: three requests (the tables are saved in warehouse/raw/eia_mecs/ and reused). EIA's robots file disallows
/archive/ and /reports/ among others, not /consumption/. License: public (EIA, read 1). MECS's next survey is fielded in
2027; 2022 is the latest.
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "eia_mecs"
SOURCE = "eia:mecs"
SURVEY = 2022
PAGE = f"https://www.eia.gov/consumption/manufacturing/data/{SURVEY}/"
BASE = PAGE + "xls/"
TABLE = "eia_mecs_manufacturing"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
X_COLS = ["x_naics", "x_region", "x_table", "x_mark"]
CODES = {"*", "D", "Q", "NA", "W", "X"}
MARKS = {"h"}
REGIONS = {"Total United States": ("us", "US"), "Northeast Census Region": ("northeast", ""), "Midwest Census Region": ("midwest", ""),
           "South Census Region": ("south", ""), "West Census Region": ("west", "")}
# each table: (file, unit factor to the table's unit, unit, [(header text lowered with only letters, starts with) -> variable])
TABLES = {
    "Table 3.2": ("Table3_2.xlsx", 1.0, "TBtu", [
        ("total", "fuel_total"), ("netelectricity", "fuel_net_electricity"), ("residualfueloil", "fuel_residual_fuel_oil"),
        ("distillatefueloil", "fuel_distillate_fuel_oil"), ("naturalgas", "fuel_natural_gas"), ("hgl", "fuel_hgl"), ("coal", "fuel_coal"),
        ("cokeandbreeze", "fuel_coke_and_breeze"), ("hydrogen", "fuel_hydrogen"), ("other", "fuel_other")]),
    "Table 11.1": ("Table11_1.xlsx", 1000.0, "MWh", [
        ("purchases", "elec_purchases"), ("transfersin", "elec_transfers_in"), ("totalonsitegeneration", "elec_onsite_generation"),
        ("salesandtransfersoffsite", "elec_sales_transfers_offsite"), ("netdemandforelectricity", "elec_net_demand")]),
    "Table 11.3": ("Table11_3.xlsx", 1000.0, "MWh", [
        ("totalonsitegeneration", "gen_total"), ("cogeneration", "gen_cogeneration"), ("renewableenergy", "gen_renewable"), ("other", "gen_other")]),
}


def letters(s):
    return re.sub(r"[^a-z]", "", str(s).lower()) if not pd.isna(s) else ""


def columns(v, h, name, wanted):
    """The table's columns: header text joined over the four rows ending at h, each matched to a variable once."""
    heads = {}
    for j in range(2, v.shape[1]):
        heads[j] = "".join(letters(v.iat[i, j]) for i in range(max(0, h - 3), h + 1))
    out = {}
    for key, var in wanted:
        hit = [j for j, t in heads.items() if t.startswith(key) and j not in out.values()]
        # a footnote letter follows each name (electricityb): the shortest header that starts with the key is the column
        hit = sorted(hit, key=lambda j: len(heads[j]))
        if not hit:
            raise RuntimeError(f"{name}: no column for {var} ({key}); headers {heads}")
        out[var] = hit[0]
    return out


def parse(content, name, base, counts):
    """The rows of one table, a census region block at a time."""
    fname, factor, unit, wanted = TABLES[name]
    v = pd.read_excel(io.BytesIO(content), sheet_name=0, header=None, dtype=object, keep_default_na=False)  # "n/a" stops the run
    title = " ".join(str(x) for x in v.iloc[:4, 0].tolist() if not pd.isna(x))
    if name not in title or str(SURVEY) not in title + str(v.iat[0, 0]):
        raise RuntimeError(f"{name}: the sheet's title is not as read: {title[:120]!r}")
    hrow = [i for i in range(min(len(v), 20)) if letters(v.iat[i, 0]) == "codea"]
    if len(hrow) != 1:
        raise RuntimeError(f"{name}: no single 'codea' header row")
    h = hrow[0]
    cols = columns(v, h, name, wanted)
    out, region, seen = [], None, set()
    for i in range(h + 1, len(v)):
        c0, c1, c2 = v.iat[i, 0], v.iat[i, 1], v.iat[i, 2]
        if isinstance(c2, str) and c2.strip() in REGIONS:
            region = c2.strip()
            continue
        code = "" if pd.isna(c0) else str(c0).strip()
        label = "" if pd.isna(c1) else str(c1).strip()
        if not code and label == "Total":
            naics, label = "total", "All manufacturing"
        elif re.fullmatch(r"\d{3,6}", code):
            naics = code
        elif not code and not label:
            continue
        else:
            raise RuntimeError(f"{name} row {i}: neither an industry nor a total: {code!r} {label!r}")
        if region is None:
            raise RuntimeError(f"{name} row {i}: an industry before any region heading")
        rslug, geo = REGIONS[region]
        if (rslug, naics) in seen:
            raise RuntimeError(f"{name}: {region} {naics} given twice")
        seen.add((rslug, naics))
        for var, j in cols.items():
            x = v.iat[i, j]
            mark = ""
            if j + 1 < v.shape[1] and isinstance(v.iat[i, j + 1], str) and v.iat[i, j + 1].strip() in MARKS:
                mark = v.iat[i, j + 1].strip()
            if pd.isna(x) or (isinstance(x, str) and x.strip() == ""):
                continue
            if isinstance(x, str):
                if x.strip() in CODES:
                    counts[x.strip()] = counts.get(x.strip(), 0) + 1
                    continue
                raise RuntimeError(f"{name} {region} {naics} {var}: not a number: {x!r}")
            out.append(dict(base, entity=f"mecs:{rslug}_{naics}", variable=var, ts_utc=f"{SURVEY}-01-01T00:00:00Z", value=float(x) * factor,
                            unit=unit, freq="P1Y", geo=geo, market="", node=label, x_naics=naics, x_region=region, x_table=name, x_mark=mark))
    if not out:
        raise RuntimeError(f"{name}: no row")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's Manufacturing Energy Consumption Survey: fuel and electricity by industry and region")
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
        rows, latest, counts, urls = [], "", {}, []
        for name, (fname, _, _, _) in TABLES.items():
            url = BASE + fname
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=120, pause=1)
            base = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
            got = parse(content, name, base, counts)
            log(f"  {name}: {len(got)} rows")
            rows += got
            urls.append(url)
            latest = max(latest, base["retrieved_at"])
        s = pd.DataFrame(rows)
        g = s[s.variable.isin(["gen_total", "elec_onsite_generation"])].pivot_table(index="entity", columns="variable", values="value")
        g = g.dropna()
        bad = g[(g.gen_total - g.elec_onsite_generation).abs() > 0.5]
        if len(bad):
            raise RuntimeError(f"Table 11.3's total onsite generation differs from Table 11.1's: {bad.head(5).to_dict('index')}")
        log(f"  onsite generation: Tables 11.1 and 11.3 agree for {len(g)} industries and regions")
        s = s[s.variable != "gen_total"]  # the same figure as elec_onsite_generation, checked above
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("an (entity, variable, ts_utc) given twice")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        coded = ", ".join(f"{k} {n}" for k, n in sorted(counts.items()))
        head = [
            f"Energy Research Warehouse (ERW): EIA, {SURVEY} Manufacturing Energy Consumption Survey (MECS), manufacturing's fuel consumption by "
            "industry, census region and energy source, and its electricity's components of net demand and onsite generation (session 2016)",
            "Shape: series (docs/datastandard.md v0). entity mecs:<region>_<naics> (us, northeast, midwest, south, west; naics the code or total); "
            "variables fuel_<source> (TBtu, Table 3.2), elec_<component> and gen_<component> (MWh, Tables 11.1 and 11.3, their million kWh times "
            "1,000); freq P1Y; ts_utc 1 January of the survey year; geo US, or empty for a census region; node the industry as named; x_naics, "
            "x_region, x_table; x_mark h where EIA marks the figure revised.",
            f"{s.entity.nunique()} industries and regions. Cells EIA writes as codes have no row: {coded} (* an estimate less than 0.5; D withheld "
            "to avoid disclosure; Q withheld, relative standard error above 50 percent; NA not available). Nothing is filled. Hydrogen is national "
            "only; in a region it is inside Other. Fuel consumption counts some byproduct fuels twice, as EIA's note to Table 3.2 says.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_mecs.py; the latest file retrieved {latest}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, {SURVEY} Manufacturing Energy Consumption Survey (Form EIA-846), {PAGE}",
            f"  access: {', '.join(urls)}",
            "License: public (EIA: U.S. government publications are in the public domain).",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s)} rows, {s.entity.nunique()} industries and regions; codes {coded}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report=f"{SURVEY} Manufacturing Energy Consumption Survey (MECS), Tables 3.2, 11.1 and 11.3", report_url=PAGE,
                                    document_list=PAGE, license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
