#!/usr/bin/env python3
"""Build the ERW coverage table: docs/coverage.md and warehouse/metadata/coverage.csv.

Energy Research Warehouse (ERW). One row per table in warehouse/output: the
ERW equivalent of the IRW's metadata.csv (github.com/ben-domingue/irw). Every
value is read from the tables themselves (rows, provenance header) or from
erw_validate, so the files are regenerated, never edited by hand. The daily
workflow runs this after the validator.

    python warehouse/metadata/build_coverage.py

coverage.csv columns: table, iso, market, n_nodes, interval, ts_min, ts_max,
n_rows, source_report, last_run, validator_status, license, sector, derived.

derived (session 9) is "yes" for a table computed by the ERW from other ERW
tables (its header has a "Derived from:" line), else "no". A derived table's
license is the most restrictive license of its input tables (Decision 23); the
build recomputes it and fails if the table's header says otherwise.

sector (session 7) is one or more of SECTORS, ";"-separated, set per table by
the first matching rule in SECTOR_RULES. A table no rule matches fails the build:
every new table gets a sector on purpose, not by default.

Tables not on this machine (session 14): coverage describes the warehouse, and
Redivis holds every table, but a machine may hold only some of them. The CI
runner starts without the tables (they left git in session 9) and restores only
the rolling-window ones, so the ERCOT yearly history, the derived tables and, on
most days, the queues are absent there. A table that is in the previous
coverage.csv but not in warehouse/output is carried over unchanged (its CSV row
and its line in docs/coverage.md, with its own last_run), and named in a note
under the table; it is never dropped. Retiring a table is a human edit.

license (session 5 ruling) is "internal" if any of the table's sources is
licensed for internal use only, otherwise "public". Per-source licenses come
from warehouse/metadata/sources.csv, the source registry the connectors keep;
the rule itself is stated in docs/datastandard.md. A table whose source is not
in the registry fails the build rather than being guessed public.
"""

import glob
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "validate"))
import erw_validate  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")
DOC = os.path.join(ROOT, "docs", "coverage.md")
CSV = os.path.join(HERE, "coverage.csv")
SOURCES = os.path.join(HERE, "sources.csv")

ISO_LABEL = {"ercot": "ERCOT", "caiso": "CAISO", "nyiso": "NYISO", "miso": "MISO",
             "spp": "SPP", "isone": "ISO-NE", "pjm": "PJM"}
# EIA-930 balancing authority codes, labelled by the ISO they are
BA_LABEL = {"ciso": "CAISO", "erco": "ERCOT", "isne": "ISO-NE", "miso": "MISO", "nyis": "NYISO",
            "pjm": "PJM", "swpp": "SPP", "us48": "US48"}
CSV_COLS = ["table", "iso", "market", "n_nodes", "interval", "ts_min", "ts_max", "n_rows",
            "source_report", "last_run", "validator_status", "license", "sector", "derived"]
# erw.filter(sector=...) vocabulary (session 7)
SECTORS = ["power", "gas", "oil", "products", "lng", "coal", "uranium", "carbon", "capacity",
           "metals", "equities", "news", "deals", "datacenters"]
# (table name pattern, sectors), first match wins
SECTOR_RULES = [
    (r"^(caiso|ercot|isone|miso|nyiso|spp)_(dam|rtm)_", "power"),
    (r"^pjm_(dam|rtm)_", "power"),
    (r"^eia930_", "power"),
    (r"^pjm_rpm_capacity_prices$", "capacity"),
    (r"^eia_fuel_spot_prices$", "oil;gas"),
    (r"^eia_(product_spot|retail_fuel)_prices$", "products"),
    (r"^eia_petroleum_(trade|stocks)_weekly$", "oil;products"),
    (r"^eia_lng_exports_monthly$", "lng"),
    (r"^(carb|rggi)_auction_allowance_prices$", "carbon"),
    (r"^fred_daily_spot_prices$", "oil;gas"),
    (r"^fred_imf_commodity_prices$", "gas;lng;coal;uranium;metals"),
    (r"^news_", "news"),
    # session 8
    (r"^eia860m_(operating|planned|retired)_generators$", "power"),
    (r"^[a-z]+_interconnection_queue$", "power"),
    (r"^eia_retail_electricity_prices$", "power"),
    (r"^eia_crude_(first_purchase_prices|imports_by_country)$", "oil"),
    (r"^eia_padd_crude_pipeline_flows$", "oil"),
    (r"^portwatch_chokepoint_transits$", "oil;lng"),
    # session 9, derived
    (r"^ercot_peak_premium_(annual|monthly)$", "power"),
    # session 15: the deal tracker (tool 6)
    (r"^energy_deals(_evidence)?$", "deals"),
    # session 16: the project map (tool 3) and the datacenter power tracker (tool 4)
    (r"^energy_projects$", "power"),
    (r"^datacenter_projects(_evidence)?$", "power;datacenters"),
]


def load_licenses():
    if not os.path.exists(SOURCES):
        raise FileNotFoundError(f"{SOURCES} is missing; the connectors write it")
    reg = pd.read_csv(SOURCES, dtype=str, keep_default_na=False)
    return dict(zip(reg["source"], reg["license"]))


def iso_of(table):
    parts = table.split("_")
    if parts[0] == "eia930":
        return BA_LABEL.get(parts[1], parts[1].upper())
    if parts[0] in ("eia", "carb", "rggi", "fred", "eia860m", "portwatch", "energy", "datacenter"):
        return "none"  # not an ISO series ("n/a" would read back as missing)
    return ISO_LABEL.get(parts[0], parts[0])


def sector_of(table):
    for pat, sectors in SECTOR_RULES:
        if re.match(pat, table):
            bad = [s for s in sectors.split(";") if s not in SECTORS]
            if bad:
                raise ValueError(f"{table}: sectors {bad} are not in {SECTORS}")
            return sectors
    raise ValueError(f"{table}: no sector rule in build_coverage.SECTOR_RULES matches; add one")


def derived_from(header):
    """Input tables of a derived table, from its 'Derived from:' header line; None if not derived."""
    for h in header:
        h = h.lstrip("#").strip()
        if h.startswith("Derived from:"):
            return [t.strip() for t in h.split(":", 1)[1].split(";") if t.strip()]
    return None


def declared_license(header):
    """A table may declare its own license in a 'License: public|internal' header line
    (session 7: news_index is public although its outlets' text is internal)."""
    for h in header:
        h = h.lstrip("#").strip()  # header lines arrive with their leading '# '
        m = re.match(r"\s*License: (public|internal)[.\s]", h + " ")
        if m:
            return m.group(1)
    return None


def last_run(header):
    """Run id of the run that last wrote the file, from its 'Retrieved:' line, as ISO UTC."""
    for h in header:
        m = re.search(r"Retrieved: (\d{8}T\d{6}Z)", h)
        if m:
            t = pd.to_datetime(m.group(1), format="%Y%m%dT%H%M%SZ", utc=True)
            return t.strftime("%Y-%m-%dT%H:%M:%SZ")
    return ""


def events_row(path, header, df, licenses, status):
    """Coverage for an events table (session 6): times from event_date, counts of sources."""
    table = os.path.splitext(os.path.basename(path))[0]
    d = df["event_date"].where(df["event_date"].str.contains("T"), df["event_date"] + "T00:00:00Z")
    ts = pd.to_datetime(d, format=erw_validate.TS_FMT, utc=True)
    sources = sorted(df["source"].unique())
    unknown = [s for s in sources if s not in licenses]
    if unknown:
        raise ValueError(f"{table}: sources {unknown[:5]} are not in {SOURCES}; cannot set its license")
    license_ = declared_license(header) or (
        "internal" if any(licenses[s] == "internal" for s in sources) else "public")
    return {
        "table": table, "iso": "none", "market": "", "n_nodes": len(sources), "interval": "event",
        "ts_min": ts.min().strftime("%Y-%m-%dT%H:%M:%SZ"), "ts_max": ts.max().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "n_rows": len(df), "source_report": f"{len(sources)} outlets", "last_run": last_run(header),
        "validator_status": status, "license": license_, "sector": sector_of(table),
        "_variable": "events: " + ", ".join(sorted(df["event_type"].unique())),
        "_nodes": f"{len(sources)} sources",
    }


def entities_row(path, header, df, licenses, status):
    """Coverage for an entities table (session 8): a snapshot, so ts_min and ts_max are the
    retrieval time of the snapshot; n_nodes counts entities."""
    table = os.path.splitext(os.path.basename(path))[0]
    got = pd.to_datetime(df["retrieved_at"], format=erw_validate.TS_FMT, utc=True)
    sources = sorted(df["source"].unique())
    unknown = [s for s in sources if s not in licenses]
    if unknown:
        raise ValueError(f"{table}: sources {unknown} are not in {SOURCES}; cannot set its license")
    license_ = declared_license(header) or (
        "internal" if any(licenses[s] == "internal" for s in sources) else "public")
    vint = sorted(df["vintage"].unique()) if "vintage" in df else []
    return {
        "table": table, "iso": iso_of(table), "market": "", "n_nodes": int(df["entity_id"].nunique()),
        "interval": "snapshot", "ts_min": got.min().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ts_max": got.max().strftime("%Y-%m-%dT%H:%M:%SZ"), "n_rows": len(df),
        "source_report": ";".join(sources), "last_run": last_run(header),
        "validator_status": status, "license": license_, "sector": sector_of(table),
        "_variable": "entities: " + ", ".join(sorted(df["entity_type"].unique()))
                     + (f"; vintage {', '.join(vint)}" if vint else ""),
        "_nodes": f"{df['entity_id'].nunique()} entities",
    }


def table_row(path, licenses):
    header, df = erw_validate.read(path)
    if list(df.columns[:2]) == ["entity_id", "entity_type"]:
        report = erw_validate.validate(path)
        n_err, n_warn = len(report["errors"]), len(report["warnings"])
        status = "pass" if not n_err else f"blocked ({n_err} errors)"
        return entities_row(path, header, df, licenses, status + (f", {n_warn} warnings" if n_warn else ""))
    if "event_id" in df.columns:
        report = erw_validate.validate(path)
        n_err, n_warn = len(report["errors"]), len(report["warnings"])
        status = "pass" if not n_err else f"blocked ({n_err} errors)"
        return events_row(path, header, df, licenses, status + (f", {n_warn} warnings" if n_warn else ""))
    report = erw_validate.validate(path)
    n_err, n_warn = len(report["errors"]), len(report["warnings"])
    status = "pass" if not n_err else f"blocked ({n_err} errors)"
    if n_warn:
        status += f", {n_warn} warnings"
    table = os.path.splitext(os.path.basename(path))[0]
    ts = pd.to_datetime(df["ts_utc"], format=erw_validate.TS_FMT, utc=True)
    sources = sorted(df["source"].unique())
    unknown = [s for s in sources if s not in licenses]
    if unknown:
        raise ValueError(f"{table}: sources {unknown} are not in {SOURCES}; cannot set its license")
    license_ = declared_license(header) or (
        "internal" if any(licenses[s] == "internal" for s in sources) else "public")
    nodes = sorted(n for n in df["node"].unique() if n) if "node" in df else []
    return {
        "table": table,
        "iso": iso_of(table),
        "market": ";".join(sorted(m for m in df["market"].unique() if m)) if "market" in df else "",
        "n_nodes": len(nodes) if nodes else int(df["entity"].nunique()),
        "interval": ";".join(sorted(df["freq"].unique())) if "freq" in df else "",
        "ts_min": ts.min().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ts_max": ts.max().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "n_rows": len(df),
        "source_report": ";".join(sorted(df["source"].unique())),
        "last_run": last_run(header),
        "validator_status": status,
        "license": license_,
        "sector": sector_of(table),
        "_derived_from": derived_from(header),
        # for the markdown only
        "_variable": ", ".join(sorted(df["variable"].unique())),
        "_nodes": ", ".join(nodes) if nodes else ", ".join(sorted(df["entity"].unique())),
    }


def apply_derived(rows):
    """Mark derived tables and check their license against their inputs (Decision 23)."""
    by = {r["table"]: r for r in rows}
    for r in rows:
        inputs = r.pop("_derived_from", None)
        r["derived"] = "yes" if inputs is not None else "no"
        if inputs is None:
            continue
        missing = [t for t in inputs if t not in by]
        if missing:
            raise ValueError(f"{r['table']}: input tables {missing} are not in warehouse/output")
        want = "internal" if any(by[t]["license"] == "internal" for t in inputs) else "public"
        if r["license"] != want:
            raise ValueError(f"{r['table']}: license {r['license']}, but its inputs make it {want}")
    return rows


def carried_over(present):
    """Rows of the previous coverage for tables not in warehouse/output on this machine:
    (CSV rows, {table: its line in docs/coverage.md})."""
    if not os.path.exists(CSV):
        return [], {}
    prev = pd.read_csv(CSV, dtype=str, keep_default_na=False)
    gone = prev[~prev["table"].isin(present)].to_dict("records")
    md = {}
    if os.path.exists(DOC):
        with open(DOC, encoding="utf-8") as f:
            for line in f:
                m = re.match(r"^\| `([a-z0-9_]+)` \|", line)
                if m:
                    md[m.group(1)] = line.rstrip("\n")
    lost = [r["table"] for r in gone if r["table"] not in md]
    if lost:
        raise ValueError(f"cannot carry over {lost}: no line for them in {os.path.relpath(DOC, ROOT)}")
    return gone, md


def main():
    licenses = load_licenses()
    rows = apply_derived([table_row(p, licenses) for p in sorted(glob.glob(os.path.join(OUT, "*.csv")))])
    carried, carried_md = carried_over({r["table"] for r in rows})
    if carried:
        print(f"carried over from the previous coverage (not in warehouse/output here): "
              f"{len(carried)} tables: {', '.join(r['table'] for r in carried)}")
    out_rows = sorted([{c: r[c] for c in CSV_COLS} for r in rows] + carried, key=lambda r: r["table"])
    pd.DataFrame(out_rows, columns=CSV_COLS).to_csv(CSV, index=False, lineterminator="\n")

    md_cols = ["Table", "ISO", "Market", "Variable", "Nodes", "Interval",
               "First interval (UTC)", "Last interval (UTC)", "Rows", "Source report",
               "Last run (UTC)", "Validator", "License", "Sector", "Derived"]
    lines = [
        "# ERW coverage",
        "",
        "What the Energy Research Warehouse (ERW) holds today: one row per table in "
        "`warehouse/output/`. The machine-readable copy is `warehouse/metadata/coverage.csv`, the "
        "ERW equivalent of the metadata table the IRW (Item Response Warehouse) calls "
        "`metadata.csv`.",
        "",
        "**Generated, do not edit by hand.** Rebuilt by the daily workflow, or with "
        "`python warehouse/metadata/build_coverage.py`. Every value comes from the table's own "
        "rows, its provenance header, or `erw_validate.py`. Interval timestamps are interval "
        "starts; day-ahead tables can run past today because a published next-day auction is "
        "included. `License` is `public` or `internal` (internal: licensed for internal use "
        "only, such as PJM data; never shown on the public site). `Sector` is what "
        "`erw.filter(sector=...)` matches: power, gas, oil, products, lng, coal, uranium, "
        "carbon, capacity, metals, equities, news. `Derived` is yes for a table the ERW computes "
        "from other ERW tables (method in `docs/methods/`).",
        "",
        "| " + " | ".join(md_cols) + " |",
        "|" + "|".join("---" for _ in md_cols) + "|",
    ]
    built = {r["table"]: r for r in rows}
    for name in sorted(list(built) + [r["table"] for r in carried]):
        if name not in built:
            lines.append(carried_md[name])
            continue
        r = built[name]
        cells = [f"`{r['table']}`", r["iso"], r["market"], r["_variable"],
                 f"{r['n_nodes']}: {r['_nodes']}", r["interval"],
                 r["ts_min"].replace("T", " ").rstrip("Z"), r["ts_max"].replace("T", " ").rstrip("Z"),
                 f"{r['n_rows']:,}", r["source_report"].replace(";", "; "),
                 r["last_run"].replace("T", " ").rstrip("Z"), r["validator_status"], r["license"], r["sector"].replace(";", ", "), r["derived"]]
        lines.append("| " + " | ".join(str(c).replace("|", "\\|") for c in cells) + " |")
    missing = [f"{label} {m.upper()}" for iso, label in ISO_LABEL.items() for m in ("dam", "rtm")
               if not glob.glob(os.path.join(OUT, f"{iso}_{m}_*.csv"))]
    missing += [f"EIA-930 {BA_LABEL[b]} {fam}" for b in BA_LABEL for fam in ("demand", "generation")
                if not os.path.exists(os.path.join(OUT, f"eia930_{b}_{fam}.csv"))]
    if carried:
        lines += ["", f"Carried over unchanged from the previous coverage, because this run's "
                  f"`warehouse/output/` does not hold them (the daily CI runner restores only the "
                  f"rolling-window tables; every table is on Redivis): {len(carried)} tables, "
                  + ", ".join(f"`{r['table']}`" for r in carried) + "."]
    lines += ["", "Markets and series with no table: " + (", ".join(missing) if missing else "none") +
              ". PJM prices need a PJM API key, which the ERW does not have yet. Why anything else "
              "is missing is in `warehouse/metadata/run_status.csv` and the connector's run log in "
              "`warehouse/output/logs/`.", ""]
    with open(DOC, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    print(f"wrote {os.path.relpath(DOC, ROOT)} and {os.path.relpath(CSV, ROOT)}: {len(out_rows)} tables "
          f"({len(rows)} built here, {len(carried)} carried over)")


if __name__ == "__main__":
    main()
