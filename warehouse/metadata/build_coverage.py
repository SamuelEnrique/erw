#!/usr/bin/env python3
"""Build the ERW coverage table: docs/coverage.md and warehouse/metadata/coverage.csv.

Energy Research Warehouse (ERW). One row per table in warehouse/output: the
ERW equivalent of the IRW's metadata.csv (github.com/ben-domingue/irw). Every
value is read from the tables themselves (rows, provenance header) or from
erw_validate, so the files are regenerated, never edited by hand. The daily
workflow runs this after the validator.

    python warehouse/metadata/build_coverage.py

coverage.csv columns: table, iso, market, n_nodes, interval, ts_min, ts_max,
n_rows, source_report, last_run, validator_status.
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

ISO_LABEL = {"ercot": "ERCOT", "caiso": "CAISO", "nyiso": "NYISO", "miso": "MISO",
             "spp": "SPP", "isone": "ISO-NE"}
CSV_COLS = ["table", "iso", "market", "n_nodes", "interval", "ts_min", "ts_max", "n_rows",
            "source_report", "last_run", "validator_status"]


def last_run(header):
    """Run id of the run that last wrote the file, from its 'Retrieved:' line, as ISO UTC."""
    for h in header:
        m = re.search(r"Retrieved: (\d{8}T\d{6}Z)", h)
        if m:
            t = pd.to_datetime(m.group(1), format="%Y%m%dT%H%M%SZ", utc=True)
            return t.strftime("%Y-%m-%dT%H:%M:%SZ")
    return ""


def table_row(path):
    header, df = erw_validate.read(path)
    report = erw_validate.validate(path)
    n_err, n_warn = len(report["errors"]), len(report["warnings"])
    status = "pass" if not n_err else f"blocked ({n_err} errors)"
    if n_warn:
        status += f", {n_warn} warnings"
    table = os.path.splitext(os.path.basename(path))[0]
    iso = table.split("_")[0]
    ts = pd.to_datetime(df["ts_utc"], format=erw_validate.TS_FMT, utc=True)
    return {
        "table": table,
        "iso": ISO_LABEL.get(iso, iso),
        "market": ";".join(sorted(df["market"].unique())) if "market" in df else "",
        "n_nodes": int(df["node"].nunique()) if "node" in df else int(df["entity"].nunique()),
        "interval": ";".join(sorted(df["freq"].unique())) if "freq" in df else "",
        "ts_min": ts.min().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ts_max": ts.max().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "n_rows": len(df),
        "source_report": ";".join(sorted(df["source"].unique())),
        "last_run": last_run(header),
        "validator_status": status,
        # for the markdown only
        "_variable": ", ".join(sorted(df["variable"].unique())),
        "_nodes": ", ".join(sorted(df["node"].unique())) if "node" in df else "",
    }


def main():
    rows = [table_row(p) for p in sorted(glob.glob(os.path.join(OUT, "*.csv")))]
    pd.DataFrame(rows, columns=CSV_COLS).to_csv(CSV, index=False, lineterminator="\n")

    md_cols = ["Table", "ISO", "Market", "Variable", "Nodes", "Interval",
               "First interval (UTC)", "Last interval (UTC)", "Rows", "Source report",
               "Last run (UTC)", "Validator"]
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
        "included.",
        "",
        "| " + " | ".join(md_cols) + " |",
        "|" + "|".join("---" for _ in md_cols) + "|",
    ]
    for r in rows:
        cells = [f"`{r['table']}`", r["iso"], r["market"], r["_variable"],
                 f"{r['n_nodes']}: {r['_nodes']}", r["interval"],
                 r["ts_min"].replace("T", " ").rstrip("Z"), r["ts_max"].replace("T", " ").rstrip("Z"),
                 f"{r['n_rows']:,}", r["source_report"].replace(";", "; "),
                 r["last_run"].replace("T", " ").rstrip("Z"), r["validator_status"]]
        lines.append("| " + " | ".join(str(c).replace("|", "\\|") for c in cells) + " |")
    missing = [f"{label} {m.upper()}" for iso, label in ISO_LABEL.items() for m in ("dam", "rtm")
               if not glob.glob(os.path.join(OUT, f"{iso}_{m}_*.csv"))]
    lines += ["", "Markets with no table: " + (", ".join(missing) if missing else "none") +
              ". PJM is not covered: its data API needs a key the ERW does not have yet. Why a "
              "market is missing is in the latest session report and the ISO's run log in "
              "`warehouse/output/logs/`.", ""]
    with open(DOC, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    print(f"wrote {os.path.relpath(DOC, ROOT)} and {os.path.relpath(CSV, ROOT)}: {len(rows)} tables")


if __name__ == "__main__":
    main()
