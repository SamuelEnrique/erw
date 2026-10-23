#!/usr/bin/env python3
"""EIA-861: each distribution utility's reliability by state, a year: SAIDI, SAIFI and CAIDI under the IEEE standard and
the utility's other standard (session 695, chain 045: a public source the ERW did not hold, taken where NERC's reserve
margins wait on a reading of NERC's terms).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia861_utility_reliability.csv, from the U.S.
Energy Information Administration's Form EIA-861 annual files (Reliability_<year>.xlsx in f861<year>.zip, sheets
Reliability_States and Reliability_Territories), the zips eia861_sales.py saved:

    page   https://www.eia.gov/electricity/data/eia861/
    file   https://www.eia.gov/electricity/data/eia861/zip/f861<year>.zip   (earlier years under archive/zip/)

    entity    eia861_reliability:<utility number>:<state>, one distribution utility in one state
    variable  <standard>_<index>_<events>: standard ieee (IEEE 1366) or other (the utility's own method); index saidi
              (minutes of interruption per customer, unit minute/customer), saifi (interruptions per customer,
              interruption/customer) or caidi (minutes per interruption, minute/interruption); events with_med (all
              events, major event days included), without_med (major event days left out) or minus_los (IEEE only:
              major event days included, loss of supply removed). <standard>_customers (count): the customers the
              figures cover
    ts_utc    the data year's 1 January at 00:00:00Z; freq P1Y; geo US-<state>; node the utility's name
    x_*       EIA's own fields: utility number, state, ownership, and for each standard whether outages are recorded
              automatically and the highest distribution voltage (kV); for the other standard whether inactive accounts
              are included and whether momentary interruptions are counted

Every column is found by its headings, not by position: the sheet's layout changed in 2019 (a Short Form column) and in
2021 (a third heading row naming the events). EIA's 2015 to 2020 heading "CAIDI Minus MED" stands where the IEEE
loss-of-supply-removed CAIDI stands from 2021, and is read as that. A cell EIA leaves "." has no row; nothing is filled.
EIA's State Totals sheet (from 2023) is not taken: it is EIA's aggregate, used for the cross-check only. A key given
twice stops the run.

    python warehouse/connectors/eia861_reliability.py --years 2015 2016 ... 2025 --offline   # the saved zips only
    python warehouse/connectors/eia861_reliability.py --years 2025                           # merged on the key

Ceiling: two requests a year (the page and the zip), none when both are saved in warehouse/raw/eia861/ (session 695
asked none). EIA's robots file disallows /archive/ (session 666): a year EIA has moved there is read only from a zip
already saved, never asked for. License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy Information
Administration, Form EIA-861").
"""

import argparse
import datetime as dt
import io
import os
import sys
import traceback
import zipfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402
from eia861_sales import PAGE, UA, held_text, years_held, zip_url  # noqa: E402  the same page and zips as the sales table

NAME = "eia861_utility_reliability"
CONNECTOR = "eia861"   # the raw files of the EIA-861 zips are shared with eia861_sales.py
SOURCE = "eia:eia861:reliability"
SHEETS = ["Reliability_States", "Reliability_Territories"]
UNITS = {"saidi": "minute/customer", "saifi": "interruption/customer", "caidi": "minute/interruption", "customers": "count"}
X_COLS = ["x_utility_number", "x_state", "x_ownership", "x_ieee_auto_recorded", "x_ieee_highest_voltage_kv",
          "x_other_auto_recorded", "x_other_highest_voltage_kv", "x_other_inactive_included", "x_other_momentary"]


def cell(frame, r, c):
    v = frame.iloc[r, c]
    return "" if pd.isna(v) else str(v).strip()


def events(heading, group):
    """with_med, without_med or minus_los, from the column's own heading (2015 to 2020) or its group (2021 on)."""
    h, g = heading.lower(), group.lower()
    if "minus los" in h or "caidi minus med" in h or "loss of supply" in g:
        return "minus_los"
    if "without med" in h or g.startswith("without major"):
        return "without_med"
    if "with med" in h or g.startswith("all events"):
        return "with_med"
    return ""


def layout(frame):
    """The sheet's columns by their headings. Returns (the heading row's index, {characteristic: column},
    {variable: column}, {x field: column}); a characteristic or one of the 17 figures missing stops the run."""
    heads = [r for r in range(min(5, len(frame))) if any(cell(frame, r, c) == "Utility Number" for c in range(frame.shape[1]))]
    if not heads:
        raise RuntimeError("no heading row names 'Utility Number'")
    hr = heads[0]
    chars, figs, xs = {}, {}, {}
    std, group = "", ""
    for c in range(frame.shape[1]):
        top, low = cell(frame, 0, c), cell(frame, hr, c)
        mid = cell(frame, hr - 1, c) if hr >= 2 else ""
        if top in ("IEEE Standard", "Other Standard"):
            std, group = top.split()[0].lower(), ""
        if mid and mid != ".":
            group = mid
        name = low.lower()
        if not std:
            key = {"data year": "year", "utility number": "utility", "utility name": "name", "state": "state", "ownership": "ownership"}.get(name)
            if key:
                chars[key] = c
            continue
        index = next((i for i in ("saidi", "saifi", "caidi") if name.startswith(i)), None)
        if index:
            ev = events(low, group)
            if not ev:
                raise RuntimeError(f"column {c}: '{low}' under '{group}' names no events")
            figs[f"{std}_{index}_{ev}"] = c
        elif name == "number of customers":
            figs[f"{std}_customers"] = c
        elif name == "highest dist. voltage":
            xs[f"x_{std}_highest_voltage_kv"] = c
        elif name == "outages recorded automatically":
            xs[f"x_{std}_auto_recorded"] = c
        elif name == "inactive accounts included":
            xs["x_other_inactive_included"] = c
        elif name == "momentary interruptions":
            xs["x_other_momentary"] = c
    want = [f"ieee_{i}_{e}" for i in ("saidi", "saifi", "caidi") for e in ("with_med", "without_med", "minus_los")]
    want += [f"other_{i}_{e}" for i in ("saidi", "saifi", "caidi") for e in ("with_med", "without_med")]
    want += ["ieee_customers", "other_customers"]
    missing = [k for k in ("year", "utility", "name", "state", "ownership") if k not in chars] + [v for v in want if v not in figs]
    if missing:
        raise RuntimeError(f"the sheet's headings lack {missing}")
    return hr, chars, figs, xs


def sheet_rows(frame, year, url, retrieved):
    """One sheet, its heading rows included, as the table's rows: a row a utility, state and figure."""
    hr, ch, figs, xs = layout(frame)
    d = frame.iloc[hr + 1:]
    d = d[pd.to_numeric(d[ch["year"]], errors="coerce").eq(year)]
    text = lambda r, c: "" if pd.isna(r[c]) else str(r[c]).strip()  # noqa: E731
    out = []
    for _, r in d.iterrows():
        util, state = int(r[ch["utility"]]), text(r, ch["state"])
        base = dict(entity=f"eia861_reliability:{util}:{state}", ts_utc=f"{year}-01-01T00:00:00Z", freq="P1Y", geo=f"US-{state}",
                    market="", node=text(r, ch["name"]), source=SOURCE, source_url=url, retrieved_at=retrieved, vintage="",
                    x_utility_number=str(util), x_state=state, x_ownership=text(r, ch["ownership"]),
                    **{k: ("" if text(r, c) == "." else text(r, c)) for k, c in xs.items()})
        for var, c in figs.items():
            v = pd.to_numeric(r[c], errors="coerce")
            if pd.isna(v):      # "." in EIA's sheet: no value, no row
                continue
            out.append(dict(base, variable=var, value=float(v), unit=UNITS[var.split("_")[1]]))
    t = pd.DataFrame(out)
    for k in X_COLS:
        if len(t) and k not in t:
            t[k] = ""
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        dup = t.loc[t.duplicated(["entity", "variable", "ts_utc"]), "entity"].unique()[:5].tolist()
        raise RuntimeError(f"{year}: an (entity, variable, ts_utc) is given twice: {dup}")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA-861 distribution utilities' reliability (SAIDI, SAIFI, CAIDI) by state")
    ap.add_argument("--years", type=int, nargs="+", help="the data years (default: the newest the page links)")
    ap.add_argument("--offline", action="store_true", help="never a request: the saved page and zips, or nothing")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"eia861_reliability_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, offline=args.offline, fresh=args.years is None, headers=UA)
        html = page.decode("utf-8", errors="replace")
        years = args.years or [zip_url(html)[1]]
        frames, urls = [], []
        for y in years:
            url, year = zip_url(html, y)
            if "/archive/" in url and not ip.raw_cached(CONNECTOR, url):
                raise RuntimeError(f"{url} is under /archive/, which EIA's robots file disallows (session 666), and is not saved; not asked")
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=600)
            if content[:2] != b"PK":
                raise RuntimeError(f"{url} is not a zip (it starts {content[:20]!r})")
            xl = pd.ExcelFile(io.BytesIO(zipfile.ZipFile(io.BytesIO(content)).read(f"Reliability_{year}.xlsx")))
            if SHEETS[0] not in xl.sheet_names:
                raise RuntimeError(f"Reliability_{year}.xlsx has no {SHEETS[0]} sheet: {xl.sheet_names}")
            for s in SHEETS:
                if s in xl.sheet_names:
                    t = sheet_rows(pd.read_excel(xl, s, header=None), year, url, rec["retrieved_at"])
                    log(f"{year} {s}: {len(t):,} rows, {t['x_utility_number'].nunique() if len(t) else 0} utilities")
                    frames.append(t)
            urls.append(url)
        s = pd.concat([f for f in frames if len(f)], ignore_index=True)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a row in two sheets")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols]
        held = sorted(set(years_held(os.path.join(ip.OUT_DIR, NAME + ".csv"), years[0])) | set(years))
        header = [
            "Energy Research Warehouse (ERW): EIA-861 distribution reliability, each utility by state, a year: SAIDI, SAIFI and CAIDI under the IEEE standard and the utility's other standard (session 695)",
            "Shape: series (docs/datastandard.md v0). entity eia861_reliability:<utility>:<state>; variable <standard>_<index>_<events> (standard ieee or other; index saidi minute/customer, saifi interruption/customer, caidi minute/interruption; "
            "events with_med, without_med, minus_los) or <standard>_customers (count); ts_utc the data year's 1 January; freq P1Y; node the utility's name; x_* EIA's own fields.",
            f"Years held: {held_text(held)} (this run wrote {held_text(sorted(years))}; earlier runs' years are kept, merged on entity, variable, ts_utc). A '.' cell has no row; nothing is filled. "
            "EIA's 2015 to 2020 heading 'CAIDI Minus MED' is read as the IEEE CAIDI with loss of supply removed. EIA's State Totals sheet is not taken.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia861_reliability.py (the zips as saved by earlier runs)",
            f"Run log: warehouse/output/logs/eia861_reliability_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Form EIA-861 Annual Electric Power Industry Report (Reliability_<year>.xlsx), {PAGE}",
            f"  access: {'; '.join(urls)}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Form EIA-861").',
        ]
        ip.write_csv(s, NAME, header, log, cols=cols)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Form EIA-861 Annual Electric Power Industry Report, reliability", report_url=PAGE,
                                    document_list=PAGE, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{held_text(sorted(years))}: {len(s):,} rows"))
        print(f"{NAME}: {held_text(sorted(years))}, {len(s):,} rows, {s['x_utility_number'].nunique():,} utilities, {s['entity'].nunique():,} utility-states")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"eia861_reliability FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status("eia861_reliability", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
