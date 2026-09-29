#!/usr/bin/env python3
"""EIA-860M monthly generator inventory: operating, planned and retired generators.

Energy Research Warehouse (ERW) connector, session 8. The first tables in the
`entities` shape (docs/datastandard.md). Reads the newest monthly workbook
EIA publishes at https://www.eia.gov/electricity/data/eia860m/ (public, no
key) and writes three tables:

| table                          | EIA sheets                   | rows |
|--------------------------------|------------------------------|------|
| eia860m_operating_generators   | Operating, Operating_PR      | every generator in EIA's operating inventory (EIA status OP, SB, OA, OS) |
| eia860m_planned_generators     | Planned, Planned_PR          | every planned generator (EIA status P, L, T, U, V, TS, OT) |
| eia860m_retired_generators     | Retired, Retired_PR          | generators retired in the vintage's year or the year before |

    python warehouse/connectors/eia860.py            # only when EIA's newest vintage changed
    python warehouse/connectors/eia860.py --force    # rebuild from the newest vintage anyway

One row per generator. entity_id is `eia860:<plant id>:<generator id>`, the
same id in all three tables, so a generator that moves from planned to
operating to retired keeps its id. entity_type `generator`. name is EIA's
plant name (the generator id is its own column). capacity_mw is EIA's
nameplate capacity; net summer and winter capacity are their own columns.
operator is EIA's "Entity Name" (the reporting utility or owner).

Status: `status` uses the entities vocabulary. Operating inventory rows are
`operating` whatever EIA's code, because EIA lists them as existing capacity;
EIA's own code and its label are kept in eia_status and eia_status_label
(OP operating, SB standby, OA out of service but expected back next year, OS
out of service and not expected back). Planned rows are `under_construction`
for EIA codes U, V and TS and `planned` for P, L, T and OT. Retired rows are
`retired`. status_date is the first day of EIA's operating month (operating),
empty for planned rows (planned_operation_date holds EIA's planned month), and
the first day of the retirement month (retired). EIA gives months, not days.

EIA's codes are kept unchanged (prime_mover, energy_source, sector,
balancing_authority, eia_status). Readable labels are added from the EIA-860
form instructions (https://www.eia.gov/survey/form/eia_860/instructions.pdf):
prime_mover_label, energy_source_label, and technology_group, a short grouping
of EIA's own `technology` text. A code or technology not in these tables fails
the run, so a new EIA code is noticed, not mislabeled.

Every row carries the vintage (the inventory month, YYYY-MM) and the workbook
URL. Each table is a snapshot of one vintage: a new vintage replaces the
table's rows (a generator that retired must leave the operating table), and
earlier vintages remain in git history and in the raw files. The monthly
cadence: run_daily.sh runs this every day; it reads EIA's page and writes only
when the newest published vintage differs from the one in the tables.
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

PAGE = "https://www.eia.gov/electricity/data/eia860m/"
BASE = "https://www.eia.gov"
UA = {"User-Agent": "Mozilla/5.0 (ERW research warehouse)"}
SOURCE = "eia:860m"
INSTRUCTIONS = "https://www.eia.gov/survey/form/eia_860/instructions.pdf"
MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august",
          "september", "october", "november", "december"]
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status",
               "status_date", "operator", "source"]
EXTRA_COLS = ["source_url", "retrieved_at", "vintage", "plant_id", "generator_id", "utility_id",
              "state", "county", "balancing_authority", "sector", "technology", "technology_group",
              "prime_mover", "prime_mover_label", "energy_source", "energy_source_label",
              "nameplate_mw", "net_summer_mw", "net_winter_mw", "eia_status", "eia_status_label"]

PRIME_MOVERS = {
    "BA": "Energy storage, battery", "CE": "Energy storage, compressed air",
    "CP": "Energy storage, concentrated solar power", "FW": "Energy storage, flywheel",
    "PS": "Energy storage, reversible hydraulic turbine (pumped storage)", "ES": "Energy storage, other",
    "ST": "Steam turbine", "GT": "Combustion (gas) turbine", "IC": "Internal combustion engine",
    "CA": "Combined cycle steam part", "CT": "Combined cycle combustion turbine part",
    "CS": "Combined cycle single shaft", "CC": "Combined cycle total unit",
    "HA": "Hydrokinetic, axial flow turbine", "HB": "Hydrokinetic, wave buoy", "HK": "Hydrokinetic, other",
    "HY": "Hydraulic turbine (conventional hydro)", "BT": "Turbines used in a binary cycle (geothermal)",
    "PV": "Photovoltaic", "WT": "Wind turbine, onshore", "WS": "Wind turbine, offshore",
    "FC": "Fuel cell", "OT": "Other",
}
ENERGY_SOURCES = {
    "AB": "Agricultural by-products", "ANT": "Anthracite coal", "BFG": "Blast furnace gas",
    "BIT": "Bituminous coal", "BLQ": "Black liquor", "DFO": "Distillate fuel oil", "GEO": "Geothermal",
    "H2": "Hydrogen", "JF": "Jet fuel", "KER": "Kerosene", "LFG": "Landfill gas", "LIG": "Lignite coal",
    "MSB": "Municipal solid waste, biogenic", "MSN": "Municipal solid waste, non-biogenic",
    "MSW": "Municipal solid waste", "MWH": "Electricity used for energy storage", "NG": "Natural gas",
    "NUC": "Nuclear", "OBG": "Other biomass gas", "OBL": "Other biomass liquids",
    "OBS": "Other biomass solids", "OG": "Other gas", "OTH": "Other", "PC": "Petroleum coke",
    "PG": "Gaseous propane", "PUR": "Purchased steam", "RC": "Refined coal", "RFO": "Residual fuel oil",
    "SC": "Coal-based synfuel", "SGC": "Coal-derived synthesis gas",
    "SGP": "Synthesis gas from petroleum coke", "SLW": "Sludge waste", "SUB": "Subbituminous coal",
    "SUN": "Solar", "TDF": "Tire-derived fuels", "WAT": "Water", "WC": "Waste/other coal",
    "WDL": "Wood waste liquids", "WDS": "Wood/wood waste solids", "WH": "Waste heat", "WND": "Wind",
    "WO": "Waste/other oil",
}
# EIA's `Technology` text -> a short group for maps and filters
TECH_GROUPS = {
    "Solar Photovoltaic": "solar", "Solar Thermal with Energy Storage": "solar",
    "Solar Thermal without Energy Storage": "solar",
    "Onshore Wind Turbine": "wind", "Offshore Wind Turbine": "wind",
    "Batteries": "storage", "Flywheels": "storage", "Hydroelectric Pumped Storage": "storage",
    "Natural Gas with Compressed Air Storage": "storage",
    "Natural Gas Fired Combined Cycle": "natural_gas", "Natural Gas Fired Combustion Turbine": "natural_gas",
    "Natural Gas Internal Combustion Engine": "natural_gas", "Natural Gas Steam Turbine": "natural_gas",
    "Other Natural Gas": "natural_gas",
    "Conventional Steam Coal": "coal", "Coal Integrated Gasification Combined Cycle": "coal",
    "Nuclear": "nuclear", "Conventional Hydroelectric": "hydro", "Geothermal": "geothermal",
    "Petroleum Liquids": "petroleum", "Petroleum Coke": "petroleum",
    "Wood/Wood Waste Biomass": "biomass", "Landfill Gas": "biomass", "Municipal Solid Waste": "biomass",
    "Other Waste Biomass": "biomass",
    "Other Gases": "other", "All Other": "other",
}
OPERATING_STATUS = {"OP": "operating", "SB": "operating", "OA": "operating", "OS": "operating"}
PLANNED_STATUS = {"P": "planned", "L": "planned", "T": "planned", "OT": "planned",
                  "U": "under_construction", "V": "under_construction", "TS": "under_construction"}

TABLES = {
    "eia860m_operating_generators": dict(sheets=["Operating", "Operating_PR"], kind="operating",
                                         title="EIA-860M operating generators"),
    "eia860m_planned_generators": dict(sheets=["Planned", "Planned_PR"], kind="planned",
                                       title="EIA-860M planned generators"),
    "eia860m_retired_generators": dict(sheets=["Retired", "Retired_PR"], kind="retired",
                                       title="EIA-860M generators retired in the vintage year and the year before"),
}


def candidates(log):
    """(year, month, url) for every monthly workbook linked on EIA's page, newest first."""
    r = ip.with_retries("EIA-860M page", lambda: requests.get(PAGE, timeout=90, headers=UA), log)
    if r.status_code != 200:
        raise RuntimeError(f"EIA-860M page HTTP {r.status_code}")
    out = set()
    for href in re.findall(r'href="([^"]+_generator(\d{4})\.xlsx)"', r.text):
        m = re.search(r"/([a-z]+)_generator(\d{4})\.xlsx$", href[0])
        if m and m.group(1) in MONTHS:
            out.add((int(m.group(2)), MONTHS.index(m.group(1)) + 1, BASE + href[0]))
    if not out:
        raise RuntimeError("EIA-860M page: no monthly generator workbook links; layout changed")
    return sorted(out, reverse=True)


def newest(log):
    """The newest link that serves a workbook. EIA links months not yet published; they
    return an HTML page, not a workbook, and are skipped (logged)."""
    today = dt.date.today()
    for year, month, url in candidates(log):
        if (year, month) > (today.year, today.month):
            log(f"  skip {year}-{month:02d}: a future month, {url}")
            continue
        r = requests.get(url, timeout=180, headers=UA)
        if r.status_code == 200 and r.content[:2] == b"PK":
            log(f"  newest published vintage {year}-{month:02d}: {url} ({len(r.content)} bytes, "
                f"last-modified {r.headers.get('last-modified')})")
            return f"{year}-{month:02d}", url, r.content
        log(f"  {year}-{month:02d} not published yet: HTTP {r.status_code}, "
            f"{r.headers.get('content-type')}, {url}")
    raise RuntimeError("EIA-860M: no linked workbook could be read")


def stored_vintage():
    vs = set()
    for name in TABLES:
        path = os.path.join(ip.OUT_DIR, name + ".csv")
        if not os.path.exists(path):
            return None
        with open(path, encoding="utf-8") as f:
            n = sum(1 for line in f if line.startswith("#"))
        vs |= set(pd.read_csv(path, skiprows=n, usecols=["vintage"], dtype=str)["vintage"])
    return vs.pop() if len(vs) == 1 else None


def num(s):
    return pd.to_numeric(s.astype(str).str.strip().replace({"": None, "nan": None}), errors="coerce")


def month_date(year, month):
    y, m = num(year), num(month)
    ok = y.notna() & m.notna()
    out = pd.Series("", index=year.index)
    out[ok] = [f"{int(a):04d}-{int(b):02d}-01" for a, b in zip(y[ok], m[ok])]
    return out


def read_sheet(content, sheet):
    d = pd.read_excel(io.BytesIO(content), sheet_name=sheet, header=2, dtype=str)
    title = pd.read_excel(io.BytesIO(content), sheet_name=sheet, header=None, nrows=1).iat[0, 0]
    d = d[d["Plant ID"].notna() & d["Plant ID"].str.strip().str.fullmatch(r"\d+")]
    return d, str(title)


def build(kind, sheets, content, vintage, url, got, log):
    frames, titles = [], []
    for sh in sheets:
        d, title = read_sheet(content, sh)
        want = f"as of {pd.Timestamp(vintage + '-01'):%B %Y}"
        if want not in title:
            raise RuntimeError(f"sheet {sh}: title {title!r} does not say {want!r}")
        titles.append(title)
        frames.append(d)
        log(f"  {sh}: {len(d)} generators ({title})")
    d = pd.concat(frames, ignore_index=True).fillna("")
    d = d.apply(lambda c: c.str.strip())
    for col, table, what in [("Prime Mover Code", PRIME_MOVERS, "prime mover"),
                             ("Energy Source Code", ENERGY_SOURCES, "energy source"),
                             ("Technology", TECH_GROUPS, "technology")]:
        bad = sorted(set(d[col]) - set(table) - {""})
        if bad:
            raise RuntimeError(f"{kind}: unknown EIA {what} value(s) {bad}; add them from {INSTRUCTIONS}")
    eid = "eia860:" + d["Plant ID"] + ":" + d["Generator ID"]
    if eid.duplicated().any():
        raise RuntimeError(f"{kind}: duplicate plant and generator ids {eid[eid.duplicated()].tolist()[:5]}")
    code = d["Status"].str.extract(r"^\(([A-Z]+)\)")[0] if "Status" in d else pd.Series("", index=d.index)
    label = d["Status"].str.replace(r"^\([A-Z]+\)\s*", "", regex=True) if "Status" in d else code
    if kind == "operating":
        status_map, status_date = OPERATING_STATUS, month_date(d["Operating Year"], d["Operating Month"])
    elif kind == "planned":
        status_map, status_date = PLANNED_STATUS, pd.Series("", index=d.index)
    else:
        code = pd.Series("RE", index=d.index)
        label = pd.Series("Retired", index=d.index)
        status_map = {"RE": "retired"}
        status_date = month_date(d["Retirement Year"], d["Retirement Month"])
    bad = sorted(set(code.fillna("")) - set(status_map))
    if bad:
        raise RuntimeError(f"{kind}: unknown EIA status code(s) {bad}")
    lat, lon = num(d["Latitude"]), num(d["Longitude"])
    out = pd.DataFrame({
        "entity_id": eid,
        "entity_type": "generator",
        "name": d["Plant Name"],
        "geo": "US-" + d["Plant State"],
        "lat": lat.map(lambda v: "" if pd.isna(v) else repr(float(v))),
        "lon": lon.map(lambda v: "" if pd.isna(v) else repr(float(v))),
        "capacity_mw": d["Nameplate Capacity (MW)"],
        "status": code.map(status_map),
        "status_date": status_date,
        "operator": d["Entity Name"],
        "source": SOURCE,
        "source_url": url, "retrieved_at": got, "vintage": vintage,
        "plant_id": d["Plant ID"], "generator_id": d["Generator ID"], "utility_id": d["Entity ID"],
        "state": d["Plant State"], "county": d["County"],
        "balancing_authority": d["Balancing Authority Code"], "sector": d["Sector"],
        "technology": d["Technology"], "technology_group": d["Technology"].map(TECH_GROUPS).fillna(""),
        "prime_mover": d["Prime Mover Code"], "prime_mover_label": d["Prime Mover Code"].map(PRIME_MOVERS).fillna(""),
        "energy_source": d["Energy Source Code"],
        "energy_source_label": d["Energy Source Code"].map(ENERGY_SOURCES).fillna(""),
        "nameplate_mw": d["Nameplate Capacity (MW)"], "net_summer_mw": d["Net Summer Capacity (MW)"],
        "net_winter_mw": d["Net Winter Capacity (MW)"],
        "eia_status": code, "eia_status_label": label,
    })
    for c in ("capacity_mw", "nameplate_mw", "net_summer_mw", "net_winter_mw"):
        v = num(out[c])
        bad = out[c][v.isna() & (out[c] != "")]
        if len(bad):
            raise RuntimeError(f"{kind}: non-numeric {c}: {bad.unique()[:5]}")
    if kind == "operating":
        out["operating_year"], out["operating_month"] = d["Operating Year"], d["Operating Month"]
        out["planned_retirement_date"] = month_date(d["Planned Retirement Year"], d["Planned Retirement Month"])
    elif kind == "planned":
        out["planned_operation_date"] = month_date(d["Planned Operation Year"], d["Planned Operation Month"])
    else:
        year = int(vintage[:4])
        keep = num(d["Retirement Year"]).isin([year, year - 1])
        log(f"  retired: {int(keep.sum())} of {len(out)} retired in {year - 1} or {year}")
        out = out[keep].copy()
        out["retirement_date"] = status_date[keep]
        out["operating_year"], out["operating_month"] = d.loc[keep, "Operating Year"], d.loc[keep, "Operating Month"]
    # session 34: EIA's "Nameplate Energy Capacity (MWh)", the energy a storage unit holds. The Operating and Retired
    # sheets carry it; the Planned sheet does not, so the planned table's column is empty (never estimated from MW)
    col = "Nameplate Energy Capacity (MWh)"
    out["energy_capacity_mwh"] = d.loc[out.index, col] if col in d else ""
    v = num(out["energy_capacity_mwh"])
    bad = out["energy_capacity_mwh"][v.isna() & (out["energy_capacity_mwh"] != "")]
    if len(bad):
        raise RuntimeError(f"{kind}: non-numeric energy_capacity_mwh: {bad.unique()[:5]}")
    return out.sort_values("entity_id"), titles


def from_raw(run_id, log):
    """Session 34: (vintage, url, content, retrieved_at) of the workbook saved by an earlier run, from its manifest,
    so a table can be rebuilt without a pull. The rows keep the retrieval time of that run."""
    folder = os.path.join(ip.ROOT, "warehouse", "raw", "eia860", run_id)
    man = pd.read_csv(os.path.join(folder, "manifest.csv"), dtype=str)
    row = man[man["file"].str.endswith(".xlsx") & (man["status"] == "200")].iloc[-1]
    m = re.search(r"/([a-z]+)_generator(\d{4})\.xlsx$", row["url"])
    vintage = f"{m.group(2)}-{MONTHS.index(m.group(1)) + 1:02d}"
    with open(os.path.join(folder, row["file"]), "rb") as f:
        content = f.read()
    import hashlib
    if hashlib.sha256(content).hexdigest() != row["sha256"]:
        raise RuntimeError(f"{row['file']}: sha256 differs from its manifest")
    log(f"  from the saved workbook {folder}/{row['file']} (vintage {vintage}, retrieved {row['retrieved_at']}), no pull")
    return vintage, row["url"], content, row["retrieved_at"]


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW EIA-860M generator inventory (entities)")
    ap.add_argument("--force", action="store_true", help="rebuild even if the vintage is unchanged")
    ap.add_argument("--from-raw", metavar="RUN_ID",
                    help="session 34: rebuild from the workbook an earlier run saved under warehouse/raw/eia860/RUN_ID, "
                         "no pull; the rows keep that run's retrieval time")
    ap.add_argument("--out-dir")
    args = ap.parse_args(argv)
    if args.out_dir:
        ip.set_out_dir(args.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"eia860_{run_id}.log"))
    if not args.from_raw:
        ip.RAW.open("eia860", run_id)
    results = []
    try:
        if args.from_raw:
            vintage, url, content, got = from_raw(args.from_raw, log)
            raw_run = args.from_raw
        else:
            vintage, url, content = newest(log)
            got, raw_run = None, run_id
        have = stored_vintage()
        if have == vintage and not args.force and not args.from_raw:
            log(f"vintage {vintage} already in the tables; nothing written")
            print(f"eia860: vintage {vintage} unchanged, nothing written")
            results = [dict(table=t, market="monthly", status="ok", detail=f"vintage {vintage} unchanged")
                       for t in TABLES]
        else:
            got = got or ip.utc_iso(pd.Timestamp.now(tz="UTC"))
            for name, cfg in TABLES.items():
                try:
                    log(f"{name}:")
                    df, titles = build(cfg["kind"], cfg["sheets"], content, vintage, url, got, log)
                    header = [
                        f"Energy Research Warehouse (ERW): {cfg['title']}, vintage {vintage}",
                        "Shape: entities (docs/datastandard.md v0). One row per generator; entity_id "
                        "eia860:<plant id>:<generator id>; capacity_mw is EIA nameplate capacity (MW).",
                        f"Retrieved: {raw_run} (UTC) by warehouse/connectors/eia860.py"
                        + (f"; rebuilt {run_id} from that run's saved workbook, no pull (--from-raw)"
                           if args.from_raw else ""),
                        f"Run log: warehouse/output/logs/eia860_{run_id}.log",
                        f"Raw files: warehouse/raw/eia860/{raw_run}/ (not in git)",
                        f"Source: {SOURCE} EIA-860M Monthly Update to the Annual Electric Generator Report, "
                        f"sheets {', '.join(cfg['sheets'])} ({'; '.join(titles)}), {url}",
                        f"  document list: {PAGE}",
                        f"Labels: prime_mover_label and energy_source_label from the EIA-860 instructions, "
                        f"{INSTRUCTIONS}; technology_group is an ERW grouping of EIA's technology text.",
                        "Snapshot: the table holds one vintage; a new vintage replaces its rows. Earlier "
                        "vintages are in git history. Dates are EIA months, written as the first of the month.",
                        "energy_capacity_mwh: EIA's Nameplate Energy Capacity (MWh), the energy a storage unit holds "
                        "(session 34); empty where EIA gives none. EIA's Planned sheet carries no such column, so it "
                        "is empty in the planned table.",
                        "License: public (EIA-PD).",
                    ]
                    ip.write_snapshot(df, name, header, log, cols=ENTITY_COLS + EXTRA_COLS
                                      + [c for c in df.columns if c not in ENTITY_COLS + EXTRA_COLS])
                    results.append(dict(table=name, market="monthly", status="ok", detail=f"vintage {vintage}"))
                except Exception:
                    tb = ip.redact(traceback.format_exc())
                    last = tb.strip().splitlines()[-1]
                    log(f"{name} FAILED, no output file written:\n{tb}")
                    print(f"eia860 {name} FAILED, no output file written: {last}", file=sys.stderr)
                    results.append(dict(table=name, market="monthly", status="failed", detail=last[:300]))
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Form EIA-860M, Monthly Update to the Annual Electric Generator Report",
                                    report_url=PAGE, document_list=PAGE,
                                    tables=[r["table"] for r in results if r["status"] == "ok"])])
    except Exception:
        tb = ip.redact(traceback.format_exc())
        last = tb.strip().splitlines()[-1]
        log(f"FAILED, no output file written:\n{tb}")
        print(f"eia860 all FAILED, no output file written: {last}", file=sys.stderr)
        results = [dict(table=t, market="monthly", status="failed", detail=last[:300]) for t in TABLES]
    ip.write_status("eia860", run_id, results)
    failures = sum(r["status"] != "ok" for r in results)
    log(f"done, failures={failures}")
    log.close()
    print(f"eia860 run log: {os.path.relpath(log.path, ip.ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
