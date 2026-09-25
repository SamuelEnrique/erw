#!/usr/bin/env python3
"""Build the ERW coverage table: docs/coverage.md and warehouse/metadata/coverage.csv.

Energy Research Warehouse (ERW). One row per table in warehouse/output: the
ERW equivalent of the IRW's metadata.csv (github.com/ben-domingue/irw). Every
value is read from the tables themselves (rows, provenance header) or from
erw_validate, so the files are regenerated, never edited by hand. The daily
workflow runs this after the validator.

    python warehouse/metadata/build_coverage.py

coverage.csv columns: table, iso, market, n_nodes, interval, ts_min, ts_max,
n_rows, source_report, last_run, validator_status, license.

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
            "source_report", "last_run", "validator_status", "license"]


def load_licenses():
    if not os.path.exists(SOURCES):
        raise FileNotFoundError(f"{SOURCES} is missing; the connectors write it")
    reg = pd.read_csv(SOURCES, dtype=str, keep_default_na=False)
    return dict(zip(reg["source"], reg["license"]))


def iso_of(table):
    parts = table.split("_")
    if parts[0] == "eia930":
        return BA_LABEL.get(parts[1], parts[1].upper())
    if parts[0] == "eia":
        return "none"  # not an ISO series ("n/a" would read back as missing)
    return ISO_LABEL.get(parts[0], parts[0])


def last_run(header):
    """Run id of the run that last wrote the file, from its 'Retrieved:' line, as ISO UTC."""
    for h in header:
        m = re.search(r"Retrieved: (\d{8}T\d{6}Z)", h)
        if m:
            t = pd.to_datetime(m.group(1), format="%Y%m%dT%H%M%SZ", utc=True)
            return t.strftime("%Y-%m-%dT%H:%M:%SZ")
    return ""


def table_row(path, licenses):
    header, df = erw_validate.read(path)
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
    license_ = "internal" if any(licenses[s] == "internal" for s in sources) else "public"
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
        # for the markdown only
        "_variable": ", ".join(sorted(df["variable"].unique())),
        "_nodes": ", ".join(nodes) if nodes else ", ".join(sorted(df["entity"].unique())),
    }


def main():
    licenses = load_licenses()
    rows = [table_row(p, licenses) for p in sorted(glob.glob(os.path.join(OUT, "*.csv")))]
    pd.DataFrame(rows, columns=CSV_COLS).to_csv(CSV, index=False, lineterminator="\n")

    md_cols = ["Table", "ISO", "Market", "Variable", "Nodes", "Interval",
               "First interval (UTC)", "Last interval (UTC)", "Rows", "Source report",
               "Last run (UTC)", "Validator", "License"]
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
        "only, such as PJM data; never shown on the public site).",
        "",
        "| " + " | ".join(md_cols) + " |",
        "|" + "|".join("---" for _ in md_cols) + "|",
    ]
    for r in rows:
        cells = [f"`{r['table']}`", r["iso"], r["market"], r["_variable"],
                 f"{r['n_nodes']}: {r['_nodes']}", r["interval"],
                 r["ts_min"].replace("T", " ").rstrip("Z"), r["ts_max"].replace("T", " ").rstrip("Z"),
                 f"{r['n_rows']:,}", r["source_report"].replace(";", "; "),
                 r["last_run"].replace("T", " ").rstrip("Z"), r["validator_status"], r["license"]]
        lines.append("| " + " | ".join(str(c).replace("|", "\\|") for c in cells) + " |")
    missing = [f"{label} {m.upper()}" for iso, label in ISO_LABEL.items() for m in ("dam", "rtm")
               if not glob.glob(os.path.join(OUT, f"{iso}_{m}_*.csv"))]
    missing += [f"EIA-930 {BA_LABEL[b]} {fam}" for b in BA_LABEL for fam in ("demand", "generation")
                if not os.path.exists(os.path.join(OUT, f"eia930_{b}_{fam}.csv"))]
    lines += ["", "Markets and series with no table: " + (", ".join(missing) if missing else "none") +
              ". PJM prices need a PJM API key, which the ERW does not have yet. Why anything else "
              "is missing is in `warehouse/metadata/run_status.csv` and the connector's run log in "
              "`warehouse/output/logs/`.", ""]
    with open(DOC, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    print(f"wrote {os.path.relpath(DOC, ROOT)} and {os.path.relpath(CSV, ROOT)}: {len(rows)} tables")


if __name__ == "__main__":
    main()
