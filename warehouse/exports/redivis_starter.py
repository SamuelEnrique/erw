#!/usr/bin/env python3
"""A starter dataset for Redivis's datapages organization (session 59, for Ben Domingue): one clean public table, EIA-930
hourly demand for the seven US ISOs, calendar years 2019 to 2025, with its codebook, source, license and citation.

Energy Research Warehouse (ERW). Writes exports/redivis-starter/:

    eia930_iso_hourly_demand_2019_2025.csv   the table: a plain CSV with one header row of column names
    codebook.csv                             every column: name, type, unit, description
    README.md                                what it is, source, license, how it was built, counts, suggested citation
    note_to_ben.txt                          three sentences to send with it

    python warehouse/exports/redivis_starter.py

The data: each ISO balancing authority's EIA-930 workbook (EIA's Hourly Electric Grid Monitor, sheet Published Hourly
Data, column Demand), as downloaded by warehouse/connectors/eia930_emissions.py and extracted beside the raw files
(warehouse/raw/eia930_emissions/<run>/<ba>_hours.csv). An hour EIA left empty is left out, never filled; the README counts
them. Nothing else is changed: EIA's values, in MW (EIA's MWh per hour), at each hour's start in UTC.
"""

import datetime as dt
import hashlib
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import eia930_emissions as em  # noqa: E402

OUT = os.path.join(ROOT, "exports", "redivis-starter")
NAME = "eia930_iso_hourly_demand_2019_2025.csv"
START, END = "2019-01-01T00:00:00Z", "2026-01-01T00:00:00Z"
ISOS = [("CISO", "CAISO", "California Independent System Operator", "America/Los_Angeles"),
        ("ERCO", "ERCOT", "Electric Reliability Council of Texas", "America/Chicago"),
        ("ISNE", "ISO-NE", "ISO New England", "America/New_York"),
        ("MISO", "MISO", "Midcontinent Independent System Operator", "America/Chicago"),
        ("NYIS", "NYISO", "New York Independent System Operator", "America/New_York"),
        ("PJM", "PJM", "PJM Interconnection", "America/New_York"),
        ("SWPP", "SPP", "Southwest Power Pool", "America/Chicago")]
CODEBOOK = [
    ("ba", "string", "", "EIA's balancing authority code (CISO, ERCO, ISNE, MISO, NYIS, PJM, SWPP)"),
    ("iso", "string", "", "The ISO's short name (CAISO, ERCOT, ISO-NE, MISO, NYISO, PJM, SPP)"),
    ("utc_hour_start", "datetime (ISO 8601, UTC)", "", "The start of the hour, UTC. EIA labels each hour by its end; one hour is subtracted"),
    ("local_hour_start", "datetime (ISO 8601 with offset)", "", "The same instant in the ISO's own time zone (Pacific for CAISO; Central for ERCOT, MISO and SPP; Eastern for ISO-NE, NYISO and PJM), with its UTC offset"),
    ("demand_mw", "integer", "MW", "Demand served in the balancing authority's area during the hour: EIA-930's Demand, in MWh per hour, which is the hour's mean MW"),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    frames, counts, meta = [], [], []
    for ba, iso, name, tz in ISOS:
        ex = em.latest_extract(ba.lower())
        if not ex:
            raise SystemExit(f"no extract for {ba} under warehouse/raw/eia930_emissions/")
        url, lm, got = em.extract_meta(ex)
        x = em.read_extract(ex)[["ts_utc", "demand_mwh"]]
        x = x[(x["ts_utc"] >= START) & (x["ts_utc"] < END)]
        hours = len(pd.date_range(START, END, freq="h", inclusive="left"))
        missing = hours - int(x["demand_mwh"].notna().sum())
        x = x.dropna(subset=["demand_mwh"])
        t = pd.to_datetime(x["ts_utc"], utc=True)
        frames.append(pd.DataFrame({"ba": ba, "iso": iso, "utc_hour_start": t.dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                    "local_hour_start": t.dt.tz_convert(tz).map(lambda v: v.isoformat()),
                                    "demand_mw": x["demand_mwh"].round().astype("int64")}))
        counts.append((iso, name, len(x), missing, int(x["demand_mwh"].min()), int(x["demand_mwh"].max())))
        meta.append((ba, url, lm, got))
    df = pd.concat(frames, ignore_index=True).sort_values(["ba", "utc_hour_start"])
    path = os.path.join(OUT, NAME)
    df.to_csv(path, index=False, lineterminator="\n")
    sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
    pd.DataFrame(CODEBOOK, columns=["column", "type", "unit", "description"]).to_csv(os.path.join(OUT, "codebook.csv"), index=False, lineterminator="\n")
    built = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    newest = max(m[3] for m in meta)[:10]
    readme = [
        "# EIA-930 hourly demand, the seven US ISOs, 2019 to 2025",
        "",
        "A starter table for Redivis: the hourly electricity demand served in the seven US independent system operators' balancing "
        "authorities, from the U.S. Energy Information Administration's Form EIA-930 (the Hourly Electric Grid Monitor), every hour of "
        "2019 to 2025, as EIA publishes it.",
        "",
        f"- **File:** `{NAME}`. One row per ISO and hour, {len(df):,} rows; a plain CSV with one header row; sha256 `{sha}`.",
        "- **Columns:** `codebook.csv` (below too).",
        f"- **Built:** {built} by `warehouse/connectors/eia930_emissions.py` (download) and `warehouse/exports/redivis_starter.py` "
        "(this table), Energy Research Warehouse (ERW), https://github.com/SamuelEnrique/erw",
        "",
        "## Codebook",
        "",
        "| Column | Type | Unit | Description |",
        "|---|---|---|---|",
        *[f"| `{c}` | {t} | {u} | {d} |" for c, t, u, d in CODEBOOK],
        "",
        "## Rows and gaps",
        "",
        "Each ISO has 61,368 hours in 2019 to 2025. An hour EIA left empty is left out, never filled.",
        "",
        "| ISO | Balancing authority | Rows | Hours EIA left empty | Lowest hour, MW | Highest hour, MW |",
        "|---|---|---|---|---|---|",
        *[f"| {i} | {n} | {r:,} | {m} | {lo:,} | {hi:,} |" for i, n, r, m, lo, hi in counts],
        "",
        "## Source",
        "",
        "U.S. Energy Information Administration, Form EIA-930, Hourly Electric Grid Monitor (https://www.eia.gov/electricity/gridmonitor/about): "
        "each balancing authority's workbook, sheet Published Hourly Data, column Demand. The workbooks used:",
        "",
        *[f"- {ba}: {url} (last modified {lm}; downloaded {got})" for ba, url, lm, got in meta],
        "",
        "Notes: EIA labels each hour by its end; `utc_hour_start` is that label less one hour. EIA's Demand is in MWh for the hour, which is "
        "the hour's mean MW. EIA revises recent data; 2019 to 2025 is past its usual revision window, but values can still change in a "
        "later workbook.",
        "",
        "## License",
        "",
        "Public domain. EIA's Copyrights and Reuse page (https://www.eia.gov/about/copyrights_reuse.php): \"U.S. government publications are "
        "in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, "
        "reports, graphs, charts, and other information products ... if you use or reproduce any of our information products, you should use "
        "an acknowledgment, which includes the publication date\".",
        "",
        "## Suggested citation",
        "",
        f"U.S. Energy Information Administration, Form EIA-930 Hourly Electric Grid Monitor, balancing authority workbooks (accessed {newest}). "
        f"Hourly demand for the seven US ISOs, 2019 to 2025, prepared by the Energy Research Warehouse (ERW), {built}, "
        "https://github.com/SamuelEnrique/erw.",
        "",
    ]
    open(os.path.join(OUT, "README.md"), "w", encoding="utf-8", newline="\n").write("\n".join(readme))
    note = ("Ben, here is a starter dataset for the datapages organization: EIA-930 hourly electricity demand for the seven US ISOs, "
            f"every hour of 2019 to 2025 ({len(df):,} rows), as one clean CSV with a codebook of every column. "
            "It is public domain U.S. government data from EIA's Hourly Electric Grid Monitor, unchanged except for labeling each hour by its "
            "start in UTC and local time, and the README gives the source workbooks, the few hours EIA left empty, and a suggested citation. "
            "If the format works for Redivis, the Energy Research Warehouse can supply more tables the same way.\n")
    open(os.path.join(OUT, "note_to_ben.txt"), "w", encoding="utf-8", newline="\n").write(note)
    print(f"wrote {os.path.relpath(OUT, ROOT)}: {len(df):,} rows; " + "; ".join(f"{i} {r:,} ({m} empty)" for i, _, r, m, _, _ in counts))


if __name__ == "__main__":
    main()
