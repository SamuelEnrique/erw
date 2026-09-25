#!/usr/bin/env python3
"""Build docs/coverage.md: one row per table in warehouse/output.

Energy Research Warehouse (ERW). The seed of the metadata table the IRW calls
metadata.csv (github.com/ben-domingue/irw). Every value is read from the
output files themselves (rows, header comments) or from erw_validate, so the
table is regenerated rather than edited:

    python warehouse/validate/build_coverage.py
"""

import glob
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import erw_validate  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")
DOC = os.path.join(ROOT, "docs", "coverage.md")

ISO_LABEL = {"ercot": "ERCOT", "caiso": "CAISO", "nyiso": "NYISO", "miso": "MISO",
             "spp": "SPP", "isone": "ISO-NE"}


def cell(v):
    return str(v).replace("|", "\\|")


def main():
    rows = []
    for path in sorted(glob.glob(os.path.join(OUT, "*.csv"))):
        name = os.path.basename(path)
        header, df = erw_validate.read(path)
        report = erw_validate.validate(path)
        verdict = "blocked" if report["errors"] else "pass"
        detail = f"{verdict} ({len(report['errors'])} errors, {len(report['warnings'])} warnings)"
        text = [h.lstrip("# ").rstrip() for h in header]
        sources = [re.sub(r",\s*https?://\S+$", "", t[len("Source: "):]) for t in text
                   if t.startswith("Source: ")]
        window = next((t[len("Window: "):] for t in text if t.startswith("Window: ")), "")
        window = re.sub(r",\s*\[.*$", "", window)
        fwd = next((t.split(": ", 1)[1] for t in text if t.startswith("Forward DAM days")), "")
        ts = pd.to_datetime(df["ts_utc"], format=erw_validate.TS_FMT, utc=True)
        iso = name.split("_")[0]
        rows.append({
            "File": f"`{name}`",
            "ISO": ISO_LABEL.get(iso, iso),
            "Market": ", ".join(sorted(df["market"].unique())) if "market" in df else "",
            "Variable": ", ".join(sorted(df["variable"].unique())),
            "Nodes": f"{df['node'].nunique()}: " + ", ".join(sorted(df["node"].unique())),
            "Interval": ", ".join(sorted(df["freq"].unique())) if "freq" in df else "",
            "Date range (UTC, interval start)": f"{ts.min():%Y-%m-%d %H:%M} to {ts.max():%Y-%m-%d %H:%M}",
            "Operating days": window + (f"; forward DAM: {fwd}" if fwd else ""),
            "Rows": f"{len(df):,}",
            "Source report": "; ".join(sources),
            "Validator": detail,
        })
    cols = list(rows[0].keys()) if rows else []
    lines = [
        "# ERW coverage",
        "",
        "What the Energy Research Warehouse (ERW) holds today: one row per table in "
        "`warehouse/output/`. This is the seed of the metadata table the IRW (Item Response "
        "Warehouse) calls `metadata.csv`.",
        "",
        "**Generated, do not edit by hand.** Rebuild with "
        "`python warehouse/validate/build_coverage.py`. Every value comes from the table's own "
        "rows, its provenance header, or `erw_validate.py`. Row counts include any forward "
        "day-ahead days listed under operating days.",
        "",
        "| " + " | ".join(cols) + " |",
        "|" + "|".join("---" for _ in cols) + "|",
    ]
    for r in rows:
        lines.append("| " + " | ".join(cell(r[c]) for c in cols) + " |")
    missing = []
    for iso, label in ISO_LABEL.items():
        for mkt in ("dam", "rtm"):
            if not glob.glob(os.path.join(OUT, f"{iso}_{mkt}_*.csv")):
                missing.append(f"{label} {mkt.upper()}")
    lines += ["", "Markets with no table: " + (", ".join(missing) if missing else "none") +
              ". PJM is not covered: its data API needs a key the ERW does not have yet. "
              "Why any other market is missing is in the latest session report and run log.", ""]
    with open(DOC, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    print(f"wrote {os.path.relpath(DOC, ROOT)}: {len(rows)} tables")


if __name__ == "__main__":
    main()
