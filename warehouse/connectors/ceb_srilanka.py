#!/usr/bin/env python3
"""Sri Lanka's power stations, installed capacity and net generation by owner and source, and the system's day and night
maximum demand, a year, from the Ceylon Electricity Board's Statistical Digest (session 2371, chain 112: Sri Lanka's
generation, in place of PUCSL's dispatch dashboard, whose figures load only through its script chunks).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/ceb_srilanka_electricity_annual.csv, from
the PDF's third page (printed page 1, the digest's "Summary of Statistics" page reference 1) of CEB's Statistical Digest 2025 (read with
pdfplumber's table extraction), one request:

    https://www.ceb.lk/front_img/img_reports/1783568926SD-2025-Finalized-(Web-Edition).pdf

The page's three tables each give two years, 2024 (stations and capacity "Restated") and 2025:

    stations_<owner>_<source>     count of power stations
    capacity_<owner>_<source>     installed capacity, MW
    generation_<owner>_<source>   net generation, MWh (CEB's GWh times 1,000)
    max_demand_day, max_demand_night   the year's day and night maximum demand, MW

    owner     ceb, ipp (independent power producers) or all (CEB's "Total" row); source total, major_hydro,
              thermal_oil, thermal_coal, ncre_wind, ncre_mini_hydro, ncre_other (dendro, biomass and municipal solid
              waste), ncre_grid_solar, ncre_rooftop_solar, small_islands (NCRE: non-conventional renewable energy)
    entity    ceb:LK; geo LK; node Sri Lanka; ts_utc the year's 1 January; freq P1Y

generation_ipp_ncre_rooftop_solar is the energy rooftop solar exported to CEB's network (the digest's next page,
"Energy exported in GWh", from 73,050 and 108,979 consumer accounts), printed under the IPPs; rooftop solar has no
station or capacity row, so capacity_all_total leaves out its 1,141 MW (2024) and 1,935 MW (2025, provisional) given on
the summary page (session 2375's note). Small islands are a generation row only.

Each owner's sources must add to its total, and CEB's and the IPPs' totals to the "Total" row, within 1.5 in CEB's
printed units (stations, MW or GWh; CEB prints small islands to 0.1 GWh); a header not CEB's, a row not in the map, a value that is not a number or a failed check stops the
run. The percentage columns are not taken. Earlier digests are not read here: the 2023 digest's text is in CID-encoded
fonts that do not extract, and the 2022 digest's generation table merges its rows into one cell (session 2371).

    python warehouse/connectors/ceb_srilanka.py [--offline] [--out-dir DIR]

Ceiling: one request, reused from warehouse/raw/ceb_srilanka/ with --offline. www.ceb.lk's robots file allows every
path and asks a crawl delay of 30 seconds; it names no AI agent (session 2371). License: internal until a ruling:
neither the digest nor the pages read state terms of reuse.
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd
import pdfplumber

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "ceb_srilanka_electricity_annual"
CONNECTOR = "ceb_srilanka"
SOURCE = "ceb:statistical_digest"
PAGE = "https://www.ceb.lk/publication-media/other-publications/en"
URL = "https://www.ceb.lk/front_img/img_reports/1783568926SD-2025-Finalized-(Web-Edition).pdf"
SOURCES = {"total": "total", "major hydro": "major_hydro", "thermal (oil)": "thermal_oil", "thermal (coal)": "thermal_coal",
           "ncre (wind)": "ncre_wind", "ncre (mini hydro)": "ncre_mini_hydro", "ncre (other)": "ncre_other",
           "ncre (grid connected solar)": "ncre_grid_solar", "ncre(rooftop solar)": "ncre_rooftop_solar",
           "ncre (rooftop solar)": "ncre_rooftop_solar", "small islands": "small_islands"}
OWNERS = {"ceb :": "ceb", "ipp :": "ipp"}
TOL = 1.5
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage"]


def num(cell, what):
    s = (cell or "").strip()
    if not re.fullmatch(r"\d{1,3}(,\d{3})*(\.\d+)?|\d+(\.\d+)?", s):
        raise RuntimeError(f"{what}: not a number: {s!r}")
    return float(s.replace(",", ""))


def year_of(cell):
    m = re.match(r"(\d{4})", (cell or "").strip())
    if not m:
        raise RuntimeError(f"a year heading that does not read: {cell!r}")
    return int(m.group(1))


def owner_rows(table, first, cols, what):
    """{owner: {source: [value a year]}} from a table's rows after its headings; 'Total' rows go to owner all."""
    got, owner = {}, None
    for row in table[first:]:
        a, b = (row[0] or "").strip().lower(), (row[1] or "").strip().lower()
        if a.startswith("total"):
            owner, src = "all", "total"
        else:
            if a in OWNERS:
                owner = OWNERS[a]
            elif a:
                raise RuntimeError(f"{what}: an owner not in the map: {row[0]!r}")
            if b not in SOURCES:
                raise RuntimeError(f"{what}: a source not in the map: {row[1]!r}")
            src = SOURCES[b]
        if owner is None:
            raise RuntimeError(f"{what}: a row before its owner: {row}")
        got.setdefault(owner, {})[src] = [num(row[c], f"{what} {owner} {src}") for c in cols]
    for o in ("ceb", "ipp"):
        for k in range(len(cols)):
            parts = sum(v[k] for s, v in got[o].items() if s != "total")
            if abs(parts - got[o]["total"][k]) > TOL:
                raise RuntimeError(f"{what}: {o}'s sources add to {parts}, its total is {got[o]['total'][k]}")
    for k in range(len(cols)):
        if abs(got["ceb"]["total"][k] + got["ipp"]["total"][k] - got["all"]["total"][k]) > TOL:
            raise RuntimeError(f"{what}: CEB's and the IPPs' totals do not add to the Total row")
    return got


def page_rows(content, retrieved, vintage):
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        tables = None
        for page in pdf.pages[:8]:
            text = page.extract_text() or ""
            if "Total Generation" in text and "Installed Capacity (MW)" in text:
                tables = page.extract_tables()
                break
    if not tables:
        raise RuntimeError("no page holds the capacity and generation tables")
    cap = next(t for t in tables if t and "Installed Capacity (MW)" in " ".join(c or "" for c in t[0]))
    gen = next(t for t in tables if t and "Net Generation (GWh)" in " ".join(c or "" for c in t[0]))
    dem = next(t for t in tables if t and any("Maximum Demand" in (r[0] or "") for r in t))
    if (cap[0][2] or "").strip() != "No. of Power Stations" or "Installed Capacity (MW)" not in (cap[0][5] or ""):
        raise RuntimeError(f"the capacity table's header is not CEB's: {cap[0]}")
    years_cap = [year_of(cap[1][c]) for c in (2, 3)] + [year_of(cap[1][c]) for c in (5, 6)]
    years_gen = [year_of(gen[1][c]) for c in (2, 3)]
    if years_cap[:2] != years_cap[2:] or years_cap[:2] != years_gen:
        raise RuntimeError(f"the tables' years differ: {years_cap} {years_gen}")
    years = years_gen
    st = owner_rows(cap, 2, (2, 3), "stations")
    mw = owner_rows(cap, 2, (5, 6), "capacity")
    gw = owner_rows(gen, 2, (2, 3), "generation")
    out = []
    base = dict(entity="ceb:LK", freq="P1Y", geo="LK", market="", node="Sri Lanka", source=SOURCE, source_url=URL,
                retrieved_at=retrieved, vintage=vintage)
    for kind, got, unit, f in (("stations", st, "count", 1.0), ("capacity", mw, "MW", 1.0), ("generation", gw, "MWh", 1000.0)):
        for owner, d in got.items():
            for src, vals in d.items():
                for y, v in zip(years, vals):
                    out.append(dict(base, variable=f"{kind}_{owner}_{src}", ts_utc=f"{y}-01-01T00:00:00Z", value=v * f, unit=unit))
    for r in dem:
        label = (r[0] or "").strip()
        var = {"Day Maximum Demand (MW)": "max_demand_day", "Night Maximum Demand (MW)": "max_demand_night"}.get(label)
        if var:
            for y, c in zip(years, (1, 2)):
                out.append(dict(base, variable=var, ts_utc=f"{y}-01-01T00:00:00Z", value=num(r[c], label), unit="MW"))
    if not any(o["variable"] == "max_demand_night" for o in out):
        raise RuntimeError("no maximum demand rows")
    return out


def finish(rows):
    t = pd.DataFrame(rows, columns=COLS)
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("a key given twice")
    return t.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="CEB's Statistical Digest: Sri Lanka's stations, capacity, generation and maximum demand")
    ap.add_argument("--offline", action="store_true", help="the saved digest only, no request")
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
        if not args.offline and (ip.paused("ceb") or ip.paused_host("www.ceb.lk")):
            raise RuntimeError("CEB is paused (warehouse/metadata/paused_sources.csv): not requested")
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=300)
        t = finish(page_rows(content, rec.get("retrieved_at") or "", ip.vintage_of(rec)))
        header = [
            f"Energy Research Warehouse (ERW): Ceylon Electricity Board (CEB), Statistical Digest 2025, Sri Lanka's power stations, installed capacity and net generation by owner and source, and the maximum demand, {t.ts_utc.min()[:4]} and {t.ts_utc.max()[:4]} (session 2371)",
            "Shape: series (docs/datastandard.md v0). entity ceb:LK; variable stations_, capacity_ (MW) or generation_ (MWh, CEB's net GWh times 1,000) followed by <owner>_<source> (owner ceb, ipp or all; source total, major_hydro, thermal_oil, "
            "thermal_coal, ncre_wind, ncre_mini_hydro, ncre_other, ncre_grid_solar, ncre_rooftop_solar, small_islands), and max_demand_day, max_demand_night (MW); ts_utc the year's 1 January; freq P1Y; geo LK. 2024's stations and capacity are CEB's restated figures. "
            "generation_ipp_ncre_rooftop_solar is rooftop solar's energy exported to the network, not IPP output; rooftop solar has no capacity row (the summary page gives 1,141 MW for 2024 and 1,935 MW for 2025), so capacity_all_total leaves it out.",
            f"{len(t)} rows, {t.variable.nunique()} variables. Each owner's sources add to its total, and CEB's and the IPPs' to the Total row, within 1.5 in CEB's printed units (stations, MW, GWh). Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/ceb_srilanka.py; the digest retrieved {rec.get('retrieved_at') or ''}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Ceylon Electricity Board, Statistical Digest 2025 (Web Edition), the PDF's third page (printed page 1), {PAGE}",
            f"  access: {URL}",
            "License: internal. Neither the digest nor CEB's pages read state terms of reuse; internal until a ruling. Cite: Ceylon Electricity Board, Statistical Digest 2025.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Ceylon Electricity Board, Sri Lanka (CEB)",
                                    report="Statistical Digest 2025, page 3 (power stations, installed capacity, net generation, maximum demand)",
                                    report_url=PAGE, document_list=URL, license="internal", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"{CONNECTOR} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
