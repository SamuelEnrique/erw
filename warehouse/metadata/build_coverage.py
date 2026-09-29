#!/usr/bin/env python3
"""Build the ERW coverage table: docs/coverage.md and warehouse/metadata/coverage.csv.

Energy Research Warehouse (ERW). One row per table in warehouse/output: the
ERW equivalent of the IRW's metadata.csv (github.com/ben-domingue/irw). Every
value is read from the tables themselves (rows, provenance header) or from
erw_validate, so the files are regenerated, never edited by hand. The daily
workflow runs this after the validator.

    python warehouse/metadata/build_coverage.py

coverage.csv columns: table, iso, market, n_nodes, interval, ts_min, ts_max,
n_rows, source_report, last_run, validator_status, license, sector, derived, tier.

tier (session 28, Ben Domingue's review, item 6) is the table's provenance tier,
one of TIERS (docs/datastandard.md, "Provenance tiers"): source (every value as the
publisher published it, reshaped only), derived (computed by ERW code from other
tables with a documented method, no model) or model_extracted (at least one column
written by a model reading text: extraction, scoring or research). Set by the first
matching rule in TIER_RULES, else "derived" for a derived table, else "source"; a
table built from a model_extracted table (its "Derived from:" line) is
model_extracted too. A table whose rows name a model (a model_id column) or whose
header names a Claude model, but which no rule makes model_extracted, fails the
build: a model's output is never labelled as a source's.

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

Absent inputs (session 18): a derived table built without some of its inputs says so in an
"Absent inputs:" header line (energy_projects, when a queue could not be pulled); each such
line is repeated in a note under the table in docs/coverage.md.

license (session 5 ruling) is "internal" if any of the table's sources is
licensed for internal use only, otherwise "public". Per-source licenses come
from warehouse/metadata/sources.csv, the source registry the connectors keep;
the rule itself is stated in docs/datastandard.md. A table whose source is not
in the registry fails the build rather than being guessed public.
"""

import glob
import itertools
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
# Session 29: the consolidated tables and the members they replaced (warehouse/metadata/table_migrations.csv)
MIGRATIONS = os.path.join(HERE, "table_migrations.csv")
MIGRATED = (pd.read_csv(MIGRATIONS, dtype=str, keep_default_na=False).set_index("old_table")["new_table"].to_dict()
            if os.path.exists(MIGRATIONS) else {})
CSV_COLS = ["table", "iso", "market", "n_nodes", "interval", "ts_min", "ts_max", "n_rows",
            "source_report", "last_run", "validator_status", "license", "sector", "derived", "tier"]
TIERS = ["source", "derived", "model_extracted"]
# Session 28: first match wins (docs/datastandard.md, "Provenance tiers")
TIER_RULES = [
    ("model_extracted", r"^(energy_deals|datacenter_projects|policy_reads)(_evidence)?$"),  # extraction from news
    ("model_extracted", r"^energy_companies$"),           # the Thesis Builder's research and the deal parties
    ("model_extracted", r"^news_(stories|index)$"),       # the scores and headlines are the model's
    ("model_extracted", r"^policy_actions$"),             # significance, sector and why are the model's
    ("derived", r"^(energy_projects|datacenter_queue_positions|storage_capacity)$"),  # ERW code over source tables
    # session 30: the Haiku shadow scores are a model's; the cost ledger prices Anthropic's usage counts
    ("model_extracted", r"^news_scores_shadow$"),
    ("derived", r"^api_cost_ledger$"),
]
# erw.filter(sector=...) vocabulary (session 7)
SECTORS = ["power", "gas", "oil", "products", "lng", "coal", "uranium", "carbon", "capacity",
           "metals", "equities", "news", "deals", "datacenters", "platform"]  # session 30: platform (operating costs)
# (table name pattern, sectors), first match wins
SECTOR_RULES = [
    (r"^(caiso|ercot|isone|miso|nyiso|spp)_(dam|rtm)_", "power"),
    # session 29: the consolidated price tables (the EIA-930 and trader ones match the rules below)
    (r"^iso_(dam|rtm)_hub_prices$", "power"),
    (r"^ercot_all_hub_prices_history$", "power"),
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
    # session 22: the tracker's combined table and its operator and queue inputs
    (r"^datacenter_(facilities|operator_sites|queue_positions)$", "power;datacenters"),
    # session 17: written only if ERCOT publishes a request-level list (warehouse/connectors/ercot_large_load.py)
    (r"^ercot_large_load_queue$", "power;datacenters"),
    # session 18: the energy mix explorer (21), the curtailment tracker (22), consumption by sector (23)
    (r"^(eia_state_generation_monthly|state_generation_mix_monthly)$", "power"),
    (r"^((caiso|spp)_curtailment_daily|ercot_wind_solar_hsl_daily|iso_curtailment_monthly)$", "power"),
    # session 23: CAISO battery output (Today's Outlook), for the Automated Analysis storage template
    (r"^caiso_battery_storage$", "power"),
    # session 24: the policy monitor (tool 12)
    (r"^policy_(actions|reads)(_evidence)?$", "news"),
    # session 24: NWS weather at the ISO load centers, the /grid overlay
    (r"^weather_(obs|forecast)_hourly$", "power"),
    # session 25: companies found by the Thesis Builder (tool 27), the seed of the company database (tool 10)
    (r"^energy_companies$", "deals"),
    (r"^eia_retail_sales_monthly$", "power"),
    (r"^eia_sector_energy_consumption_monthly$", "power;gas;oil;coal"),
    # session 19: the trader view (24)
    (r"^([a-z]+_trader_daily|iso_rt_top_intervals)$", "power"),
    # session 30: price board v2 (derived), the Haiku shadow scores and the API cost ledger (internal)
    (r"^price_board_(latest|peak_offpeak)$", "power"),
    (r"^price_board_spreads$", "power;gas;oil"),
    (r"^price_board_carbon$", "carbon"),
    (r"^news_scores_shadow$", "news"),
    (r"^api_cost_ledger$", "platform"),
    # session 31: battery storage (EIA-930 BAT, its daily cycle, the EIA-860M battery units)
    (r"^storage_(daily_cycle|capacity)$", "power"),
]


def load_licenses():
    if not os.path.exists(SOURCES):
        raise FileNotFoundError(f"{SOURCES} is missing; the connectors write it")
    reg = pd.read_csv(SOURCES, dtype=str, keep_default_na=False)
    return dict(zip(reg["source"], reg["license"]))


def iso_of(table):
    members = [old for old, new in MIGRATED.items() if new == table]
    if members:  # session 29: a consolidated table spans its members' ISOs
        return ";".join(sorted({iso_of(m) for m in members}))
    parts = table.split("_")
    if table == "price_board_carbon":  # session 30: CARB and RGGI, no ISO
        return "none"
    if table.startswith("price_board_"):  # session 30: price board v2 spans the six public ISOs
        return "CAISO;ERCOT;ISO-NE;MISO;NYISO;SPP"
    if table in ("eia930_all_storage", "storage_daily_cycle"):  # session 31: the BAs with an EIA-930 BAT series
        return "ERCOT;ISO-NE;MISO;SPP;US48"
    if table == "storage_capacity":  # session 31: the national EIA-860M battery inventory
        return "none"
    if parts[0] == "eia930":
        return BA_LABEL.get(parts[1], parts[1].upper())
    if parts[0] in ("eia", "carb", "rggi", "fred", "eia860m", "portwatch", "energy", "datacenter", "api"):
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
            # session 29: an input named by its old name is read as the consolidated table it moved into
            return list(dict.fromkeys(MIGRATED.get(t.strip(), t.strip()) for t in h.split(":", 1)[1].split(";")
                                      if t.strip()))
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
    # session 29: validate first, then read, so a large table (the ERCOT history) is never held twice
    report = erw_validate.validate(path)
    header, df = erw_validate.read(path)
    if list(df.columns[:2]) == ["entity_id", "entity_type"]:
        n_err, n_warn = len(report["errors"]), len(report["warnings"])
        status = "pass" if not n_err else f"blocked ({n_err} errors)"
        return entities_row(path, header, df, licenses, status + (f", {n_warn} warnings" if n_warn else ""))
    if "event_id" in df.columns:
        n_err, n_warn = len(report["errors"]), len(report["warnings"])
        status = "pass" if not n_err else f"blocked ({n_err} errors)"
        return events_row(path, header, df, licenses, status + (f", {n_warn} warnings" if n_warn else ""))
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


def header_of(table):
    path = os.path.join(OUT, table + ".csv")
    with open(path, encoding="utf-8") as f:
        return [ln.lstrip("#").strip() for ln in itertools.takewhile(lambda ln: ln.startswith("#"), f)]


def tier_by_rule(table, derived):
    for tier, pat in TIER_RULES:
        if re.match(pat, table):
            return tier
    return "derived" if derived == "yes" else "source"


def apply_tiers(rows):
    """Session 28: the provenance tier of every table built here (see the module docstring)."""
    by = {r["table"]: r for r in rows}
    inputs = {}
    for r in rows:
        r["tier"] = tier_by_rule(r["table"], r["derived"])
        # the "Derived from:" inputs, separated by ";" or "," (datacenter_facilities uses commas)
        line = next((h for h in header_of(r["table"]) if h.startswith("Derived from:")), "")
        inputs[r["table"]] = [MIGRATED.get(t.strip(), t.strip()) for t in re.split(r"[;,]", line.split(":", 1)[1])
                              if t.strip()] if line else []  # session 29: old names through the map
    changed = True
    while changed:  # a table built from a model_extracted one is model_extracted
        changed = False
        for r in rows:
            if r["tier"] != "model_extracted" and any(by.get(t, {}).get("tier") == "model_extracted"
                                                       for t in inputs[r["table"]]):
                r["tier"], changed = "model_extracted", True
    for r in rows:
        header = header_of(r["table"])
        with open(os.path.join(OUT, r["table"] + ".csv"), encoding="utf-8") as f:
            cols = next(ln for ln in f if not ln.startswith("#")).rstrip(chr(13) + chr(10)).split(",")
        names_model = "model_id" in cols or any(re.search(r"(?<![a-z])claude-[a-z]", h) for h in header)
        if names_model and r["tier"] != "model_extracted":
            raise ValueError(f"{r['table']}: its rows or header name a model, but its tier is {r['tier']}; "
                             "add it to build_coverage.TIER_RULES as model_extracted")
    return rows


def carried_over(present):
    """Rows of the previous coverage for tables not in warehouse/output on this machine:
    (CSV rows, {table: its line in docs/coverage.md})."""
    if not os.path.exists(CSV):
        return [], {}
    prev = pd.read_csv(CSV, dtype=str, keep_default_na=False)
    # session 29: a table consolidated into another is gone for good, not carried over (table_migrations.csv)
    gone = prev[~prev["table"].isin(present) & ~prev["table"].isin(set(MIGRATED))].to_dict("records")
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
    rows = apply_tiers(apply_derived([table_row(p, licenses) for p in sorted(glob.glob(os.path.join(OUT, "*.csv")))]))
    carried, carried_md = carried_over({r["table"] for r in rows})
    for r in carried:  # session 28: a row carried from a coverage.csv written before the tier column
        if not r.get("tier"):
            r["tier"] = tier_by_rule(r["table"], r.get("derived", "no"))
            carried_md[r["table"]] = carried_md[r["table"]] + f" {r['tier']} |"
    if carried:
        print(f"carried over from the previous coverage (not in warehouse/output here): "
              f"{len(carried)} tables: {', '.join(r['table'] for r in carried)}")
    out_rows = sorted([{c: r[c] for c in CSV_COLS} for r in rows] + carried, key=lambda r: r["table"])
    pd.DataFrame(out_rows, columns=CSV_COLS).to_csv(CSV, index=False, lineterminator="\n")

    md_cols = ["Table", "ISO", "Market", "Variable", "Nodes", "Interval",
               "First interval (UTC)", "Last interval (UTC)", "Rows", "Source report",
               "Last run (UTC)", "Validator", "License", "Sector", "Derived", "Tier"]
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
        "from other ERW tables (method in `docs/methods/`). `Tier` is the provenance tier "
        "(`docs/datastandard.md`): `source` (as the publisher published it), `derived` (computed by ERW "
        "code, no model) or `model_extracted` (at least one column written by a model reading text).",
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
                 r["last_run"].replace("T", " ").rstrip("Z"), r["validator_status"], r["license"], r["sector"].replace(";", ", "), r["derived"], r["tier"]]
        lines.append("| " + " | ".join(str(c).replace("|", "\\|") for c in cells) + " |")
    # session 29: a member of a consolidated table counts as present when its consolidated table is
    def present(name):
        return os.path.exists(os.path.join(OUT, name + ".csv")) or (
            name in MIGRATED and os.path.exists(os.path.join(OUT, MIGRATED[name] + ".csv")))
    missing = [f"{label} {m.upper()}" for iso, label in ISO_LABEL.items() for m in ("dam", "rtm")
               if not glob.glob(os.path.join(OUT, f"{iso}_{m}_*.csv"))
               and not any(present(o) for o in MIGRATED if o.startswith(f"{iso}_{m}_"))]
    missing += [f"EIA-930 {BA_LABEL[b]} {fam}" for b in BA_LABEL for fam in ("demand", "generation")
                if not present(f"eia930_{b}_{fam}")]
    if carried:
        lines += ["", f"Carried over unchanged from the previous coverage, because this run's "
                  f"`warehouse/output/` does not hold them (the daily CI runner restores only the "
                  f"rolling-window tables; every table is on Redivis): {len(carried)} tables, "
                  + ", ".join(f"`{r['table']}`" for r in carried) + "."]
    # session 18: a derived table built without some of its inputs names them in an
    # "Absent inputs:" header line (energy_projects when a queue could not be pulled)
    absent_notes = []
    for name in sorted(built):
        with open(os.path.join(OUT, name + ".csv"), encoding="utf-8") as f:
            header = list(itertools.takewhile(lambda ln: ln.startswith("#"), f))
        for h in header:
            h = h.lstrip("#").strip()
            if h.startswith("Absent inputs:"):
                absent_notes.append(f"`{name}` was built without some inputs. {h}")
    if absent_notes:
        lines += ["", "Absent inputs (session 18): " + " ".join(absent_notes)]
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
