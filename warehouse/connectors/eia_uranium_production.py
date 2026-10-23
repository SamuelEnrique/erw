#!/usr/bin/env python3
"""EIA's Domestic Uranium Production Report (quarterly): uranium concentrate produced at each U.S. facility, a quarter;
the number of mills and plants producing it, a year; and each mill and in-situ recovery plant with its owner, place,
capacity and operating status (session 958, chain 054: the front of the nuclear fuel chain, beside
eia_uranium_marketing_annual and nrc_power_reactors).

Energy Research Warehouse (ERW) connector. Two tables from the report's four workbooks (Forms EIA-851Q and EIA-851A):

    https://www.eia.gov/uranium/production/quarterly/   (xls/qupd_tbl1.xlsx to qupd_tbl4.xlsx)

    eia_uranium_production_quarterly   series: entity eia_u3o8:<facility> (eia_u3o8:total, EIA's total row), variable
        production, unit lb (pounds of U3O8), ts_utc the quarter's first day, freq P3M (Table 1); entity
        eia_uranium_facilities:<kind>, variable facilities_producing, unit count, at the end of each year (ts_utc that
        year's 1 January, freq P1Y) and of the latest quarter (freq P3M) (Table 2); geo US-<state> for a facility in
        one state, US for the totals
    eia_uranium_facilities             entities: entity_id eia_uranium_facility:<name>; entity_type plant; name; geo
        US-<state>; capacity_mw empty; status empty (EIA's status of each period in x_status_*); operator the owner;
        x_kind mill (Table 3) or isr (Table 4), x_capacity and x_capacity_unit as EIA gives them (short tons of ore a
        day for a mill, pounds of U3O8 a year for a plant), x_location

EIA's marks have no row: "-" (none) and "." (not available or withheld). A heading not as read or a key given twice
stops the run; nothing is filled.

    python warehouse/connectors/eia_uranium_production.py [--offline]

Ceiling: four requests (the four workbooks, saved in warehouse/raw/eia_uranium_production/ and reused
offline). EIA's robots file allows /uranium/production/. License: public (EIA, record 1 of license_reads.csv).
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

SERIES, ENTITIES = "eia_uranium_production_quarterly", "eia_uranium_facilities"
CONNECTOR = "eia_uranium_production"
SOURCE = "eia:uranium_production_quarterly"
PAGE = "https://www.eia.gov/uranium/production/quarterly/"
BASE_URL = PAGE + "xls/qupd_tbl{}.xlsx"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
STATES = {"Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO", "Connecticut": "CT",
          "Delaware": "DE", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
          "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI",
          "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH",
          "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
          "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN",
          "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI",
          "Wyoming": "WY"}
KINDS = {"Mills - conventional milling": "mills_conventional", "Mills - other operations": "mills_other", "In-situ recovery plants": "isr_plants",
         "Byproduct recovery plants": "byproduct_plants", "Total": "total"}
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
               "source", "source_url", "retrieved_at", "vintage"]
SERIES_X = ["x_facility", "x_location"]


def text(v):
    return "" if v is None or (isinstance(v, float) and pd.isna(v)) else re.sub(r"\s+", " ", str(v)).strip()


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", text(s).lower()).strip("_")


def state_of(location):
    st = text(location).rsplit(", ", 1)[-1]
    return f"US-{STATES[st]}" if st in STATES else ""


def quarter_ts(label):
    m = re.fullmatch(r"Q([1-4]) (\d{4})", text(label))
    if not m:
        raise RuntimeError(f"a quarter not as read: {label!r}")
    return f"{m.group(2)}-{3 * int(m.group(1)) - 2:02d}-01T00:00:00Z"


def table1(d, base, marks):
    h = 7
    if text(d.iloc[h, 0]) != "Facility" or text(d.iloc[h, 1]) != "Location" or text(d.iloc[5, 0]) != "pounds U3O8":
        raise RuntimeError("Table 1: headings not as read")
    qs = [(j, quarter_ts(d.iloc[h, j])) for j in range(2, d.shape[1]) if text(d.iloc[h, j])]
    out = []
    for i in range(h + 1, len(d)):
        name = text(d.iloc[i, 0])
        if not name or name.startswith("Data source"):
            break
        total = name == "Total production"
        loc = text(d.iloc[i, 1])
        for j, ts in qs:
            raw = text(d.iloc[i, j])
            v = pd.to_numeric(raw, errors="coerce")
            if pd.isna(v):
                marks[raw or "blank"] = marks.get(raw or "blank", 0) + 1
                continue
            out.append(dict(base, entity="eia_u3o8:total" if total else f"eia_u3o8:{slug(name)}", variable="production", ts_utc=ts, value=float(v),
                            unit="lb", freq="P3M", geo="US" if total else state_of(loc), market="", node=name, x_facility=name, x_location=loc))
    return out


def table2(d, base):
    h = 7
    heads = [re.sub(r" [a-d]$", "", text(d.iloc[h, j])) for j in range(1, 6)]
    if text(d.iloc[h, 0]) != "End of" or heads != list(KINDS):
        raise RuntimeError(f"Table 2: headings not as read: {heads}")
    out = []
    for i in range(h + 1, len(d)):
        label = text(d.iloc[i, 0])
        if re.fullmatch(r"\d{4}", label):
            ts, freq = f"{label}-01-01T00:00:00Z", "P1Y"
        else:
            m = re.fullmatch(r"(First|Second|Third|Fourth) quarter of (\d{4})", label)
            if not m:
                break
            q = ["First", "Second", "Third", "Fourth"].index(m.group(1)) + 1
            ts, freq = f"{m.group(2)}-{3 * q - 2:02d}-01T00:00:00Z", "P3M"
        for j, kind in zip(range(1, 6), KINDS.values()):
            out.append(dict(base, entity=f"eia_uranium_facilities:{kind}", variable="facilities_producing", ts_utc=ts, value=float(d.iloc[i, j]),
                            unit="count", freq=freq, geo="US", market="", node=f"{heads[j - 1]}, end of {label}", x_facility="", x_location=""))
    return out


def plants(d, base, kind):
    owner_h, cap_h = text(d.iloc[6, 0]), text(d.iloc[6, 3]) or text(d.iloc[7, 3])
    want = "Owner" if kind == "mill" else "In-situ recovery plant owner"
    if not owner_h.startswith(want) or "apacity" not in cap_h:
        raise RuntimeError(f"Table {3 if kind == 'mill' else 4}: headings not as read: {owner_h!r} {cap_h!r}")
    unit = re.search(r"\(([^)]*)\)", cap_h)
    periods = [text(d.iloc[7, j]) for j in range(4, d.shape[1])]
    out = []
    for i in range(8, len(d)):
        owner = text(d.iloc[i, 0])
        if not owner or owner.startswith("Total") or owner.startswith("Data source"):
            break
        name, loc = text(d.iloc[i, 1]), text(d.iloc[i, 2])
        row = dict(entity_id=f"eia_uranium_facility:{slug(name)}", entity_type="plant", name=name, geo=state_of(loc), lat="", lon="",
                   capacity_mw="", status="", status_date="", operator=owner, source=base["source"], source_url=base["source_url"],
                   retrieved_at=base["retrieved_at"], vintage=base["vintage"], x_kind=kind, x_location=loc,
                   x_capacity=text(d.iloc[i, 3]), x_capacity_unit=unit.group(1) if unit else cap_h)
        for j, p in zip(range(4, d.shape[1]), periods):
            if p:
                s = text(d.iloc[i, j])
                row[f"x_status_{slug(p)}"] = "" if s in ("-", "") else s
        out.append(row)
    return out


def build(books, bases):
    marks = {}
    s = pd.DataFrame(table1(books[1], bases[1], marks) + table2(books[2], bases[2]))
    if s.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an (entity, variable, ts_utc) given twice")
    e = pd.DataFrame(plants(books[3], bases[3], "mill") + plants(books[4], bases[4], "isr"))
    if e.entity_id.duplicated().any():
        raise RuntimeError(f"a facility given twice: {e.loc[e.entity_id.duplicated(), 'entity_id'].tolist()}")
    return s, e, marks


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's Domestic Uranium Production Report, quarterly")
    ap.add_argument("--offline", action="store_true", help="the saved workbooks only, no request")
    ap.add_argument("--out-dir", help="a trial: the tables under this folder, not warehouse/output")
    ap.add_argument("--table", choices=[SERIES, ENTITIES], action="append", help="the table(s) to write (default both)")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results, names = [], args.table or [SERIES, ENTITIES]
    try:
        books, bases = {}, {}
        for n in (1, 2, 3, 4):
            url = BASE_URL.format(n)
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=120)
            books[n] = pd.read_excel(io.BytesIO(content), header=None)
            bases[n] = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        release = text(books[1].iloc[1, 0])
        s, e, marks = build(books, bases)
        common = [
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Domestic Uranium Production Report (Quarterly), Forms EIA-851Q and EIA-851A, {PAGE} ({release})",
            f"  access: {BASE_URL.format('1')} to {BASE_URL.format('4')}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Domestic Uranium Production Report").',
        ]
        if SERIES in names:
            cols = ip.SERIES_COLS + SERIES_X
            s = s[cols].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
            prod = s[s.variable == "production"]
            header = [
                "Energy Research Warehouse (ERW): EIA, Domestic Uranium Production Report: uranium concentrate produced at each U.S. facility, a quarter, and the number of facilities producing it (session 958)",
                "Shape: series (docs/datastandard.md v0). entity eia_u3o8:<facility> (eia_u3o8:total, EIA's total) variable production, unit lb (pounds of U3O8), "
                "freq P3M; entity eia_uranium_facilities:<kind> variable facilities_producing, unit count, at the end of each year (freq P1Y, ts_utc the year's "
                "1 January) and of the latest quarter (freq P3M); geo US-<state> for a facility in one state, US for the totals.",
                f"Quarters {prod.ts_utc.min()[:7]} to {prod.ts_utc.max()[:7]}: {prod.entity.nunique() - 1} facilities; counts {s[s.variable != 'production'].ts_utc.min()[:4]} on. "
                f"EIA's marks have no row: {', '.join(f'{v} {k!r}' for k, v in marks.items())} ('-' none, '.' not available or withheld). Nothing is filled.",
                f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_uranium_production.py; the workbooks retrieved {bases[1]['retrieved_at']}",
            ] + common
            ip.write_snapshot(s, SERIES, header, log, cols)
            results.append(dict(table=SERIES, market="all", status="ok", detail=f"{len(s)} rows"))
            print(f"{SERIES}: {len(s)} rows; marks {marks}")
        if ENTITIES in names:
            xs = [c for c in e.columns if c.startswith("x_")]
            e = e[ENTITY_COLS + xs].sort_values("entity_id").reset_index(drop=True)
            header = [
                "Energy Research Warehouse (ERW): EIA, Domestic Uranium Production Report: U.S. uranium mills and heap leach facilities (Table 3) and in-situ recovery plants (Table 4), owner, place, capacity and operating status (session 958)",
                "Shape: entities (docs/datastandard.md v0). entity_id eia_uranium_facility:<name>; entity_type plant; geo US-<state>; capacity_mw empty; status "
                "empty (EIA's operating status of each period in x_status_*, as EIA writes it); operator the owner; x_kind mill or isr; x_capacity and "
                "x_capacity_unit as EIA gives them.",
                f"{len(e)} facilities ({', '.join(f'{v} {k}' for k, v in e.x_kind.value_counts().items())}). Nothing is filled.",
                f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_uranium_production.py; the workbooks retrieved {bases[3]['retrieved_at']}",
            ] + common
            ip.write_snapshot(e, ENTITIES, header, log, cols=ENTITY_COLS + xs)
            results.append(dict(table=ENTITIES, market="all", status="ok", detail=f"{len(e)} facilities"))
            print(f"{ENTITIES}: {len(e)} facilities")
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Domestic Uranium Production Report (Quarterly)", report_url=PAGE, document_list=PAGE,
                                    license="public", tables=[r["table"] for r in results])])
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"{CONNECTOR} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=",".join(names), market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
