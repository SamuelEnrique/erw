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
Data), the newest copy downloaded by warehouse/connectors/eia930_emissions.py (warehouse/raw/eia930_emissions/). Three
columns: Adjusted demand (EIA's cleaned series: the reported value, with the hours EIA found anomalous or missing replaced
by its imputation), Demand (as the balancing authority reported it) and Imputed demand (EIA's imputed value, where it
imputed). The table's demand_mw is Adjusted demand; demand_reported_mw and imputed keep what EIA changed visible. A first
build of this session used Demand alone and held EIA's raw anomalies (PJM 2,147,480,000 MW in one hour, NYISO 0 MW): it
was rebuilt on Adjusted demand before anything was sent. An hour with no Adjusted demand is left out and counted.

Adjusted demand still holds hours no grid can have (PJM 224,345 MW in July 2020, above PJM's all-time peak; NYISO 0 MW;
CAISO 14 MW). They are EIA's published values and stay as published; the column suspect marks them by a stated rule
(SUSPECT_RULE), so a user can drop them in one filter. Nothing is changed or filled.
"""

import datetime as dt
import glob
import hashlib
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
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
    ("demand_mw", "integer", "MW", "Demand in the balancing authority's area during the hour: EIA-930's Adjusted demand (the reported value, with the hours EIA found anomalous or missing replaced by its imputation), in MWh per hour, which is the hour's mean MW"),
    ("demand_reported_mw", "integer", "MW", "EIA-930's Demand as the balancing authority reported it; empty where it reported none"),
    ("imputed", "boolean", "", "true where EIA imputed the hour's demand (its Imputed demand column holds a value), so demand_mw is EIA's estimate, not the reported value"),
    ("suspect", "boolean", "", "true where demand_mw is implausible by the rule in the README (below 30% of the ISO's median hour, or a single hour more than 20% above or below both the hour before and the hour after); the value is EIA's, unchanged"),
]
SUSPECT_RULE = ("below 30% of the ISO's median hour in 2019 to 2025, or a single hour more than 20% above both the hour before and the "
                "hour after, or more than 20% below both (a grid's demand does not jump and fall back within an hour)")


def suspect(start, mw):
    """True where an hour's demand is implausible by SUSPECT_RULE. start: the hours' starts (UTC); mw: demand, same index."""
    s = pd.Series(mw.to_numpy(), index=pd.DatetimeIndex(start)).sort_index()
    full = s.reindex(pd.date_range(s.index.min(), s.index.max(), freq="h"))
    prev, nxt = full.shift(1).reindex(s.index), full.shift(-1).reindex(s.index)
    flag = (s < 0.3 * s.median()) | ((s > 1.2 * prev) & (s > 1.2 * nxt)) | ((s < prev / 1.2) & (s < nxt / 1.2))
    return pd.Series(flag.reindex(pd.DatetimeIndex(start)).to_numpy(), index=mw.index)


def workbook(ba):
    """The newest saved copy of the balancing authority's EIA-930 workbook, with its manifest line (URL, Last-Modified)."""
    paths = sorted(glob.glob(os.path.join(ROOT, "warehouse", "raw", "eia930_emissions", "*", f"*_{ba}.xlsx")))
    # the newest copy that is a workbook: an interrupted download leaves a file that is not a zip (an xlsx starts PK)
    paths = [x for x in paths if open(x, "rb").read(2) == b"PK"]
    if not paths:
        raise SystemExit(f"no saved {ba} workbook under warehouse/raw/eia930_emissions/")
    p = paths[-1]
    man = pd.read_csv(os.path.join(os.path.dirname(p), "manifest.csv"), dtype=str, keep_default_na=False)
    hit = man[man["file"].str.endswith(os.path.basename(p))] if "file" in man else man.iloc[0:0]
    m = hit.iloc[-1] if len(hit) else pd.Series(dtype=str)
    return p, m.get("url", ""), m.get("last_modified", ""), m.get("retrieved_at", "")


def read_workbook(p):
    """UTC time, Demand, Imputed demand and Adjusted demand of the sheet Published Hourly Data, streamed. EIA's UTC time
    is the hour's end, as its API's period; the hour's start is one hour earlier."""
    import openpyxl
    ws = openpyxl.load_workbook(p, read_only=True)["Published Hourly Data"]
    rows = ws.iter_rows(values_only=True)
    head = list(next(rows))
    ix = {c: head.index(c) for c in ("UTC time", "Demand", "Imputed demand", "Adjusted demand")}
    out = [(r[ix["UTC time"]], r[ix["Demand"]], r[ix["Imputed demand"]], r[ix["Adjusted demand"]]) for r in rows if r[ix["UTC time"]] is not None]
    d = pd.DataFrame(out, columns=["utc", "demand", "imputed", "adjusted"])
    end = pd.to_datetime(d["utc"], utc=True)
    return d.assign(start=end - pd.Timedelta(hours=1))


def main():
    os.makedirs(OUT, exist_ok=True)
    frames, counts, meta = [], [], []
    hours = len(pd.date_range(START, END, freq="h", inclusive="left"))
    for ba, iso, name, tz in ISOS:
        p, url, lm, got = workbook(ba)
        d = read_workbook(p)
        x = d[(d["start"] >= pd.Timestamp(START)) & (d["start"] < pd.Timestamp(END))]
        adj = pd.to_numeric(x["adjusted"], errors="coerce")
        rep = pd.to_numeric(x["demand"], errors="coerce")
        imp = pd.to_numeric(x["imputed"], errors="coerce").notna()
        keep = adj.notna()
        missing = hours - int(keep.sum())
        x, adj, rep, imp = x[keep], adj[keep], rep[keep], imp[keep]
        t = x["start"]
        sus = suspect(t, adj)
        ok = adj[~sus]
        frames.append(pd.DataFrame({"ba": ba, "iso": iso, "utc_hour_start": t.dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                    "local_hour_start": t.dt.tz_convert(tz).map(lambda v: v.isoformat()),
                                    "demand_mw": adj.round().astype("int64"),
                                    "demand_reported_mw": rep.round().astype("Int64"),
                                    "imputed": imp.map({True: "true", False: "false"}),
                                    "suspect": sus.map({True: "true", False: "false"})}))
        counts.append((iso, name, len(x), missing, int(adj.min()), int(adj.max()), int(imp.sum()), int(sus.sum()), int(ok.min()), int(ok.max())))
        meta.append((ba, url, lm, got))
        print(f"  {ba}: {len(x):,} hours, {int(imp.sum())} imputed by EIA, {missing} without adjusted demand, {int(sus.sum())} suspect, {int(adj.min()):,} to {int(adj.max()):,} MW ({int(ok.min()):,} to {int(ok.max()):,} not suspect)")
    df = pd.concat(frames, ignore_index=True).sort_values(["ba", "utc_hour_start"])
    path = os.path.join(OUT, NAME)
    df.to_csv(path, index=False, lineterminator="\n")
    sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
    pd.DataFrame(CODEBOOK, columns=["column", "type", "unit", "description"]).to_csv(os.path.join(OUT, "codebook.csv"), index=False, lineterminator="\n")
    built = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    newest = max((m[3] or built) for m in meta)[:10]
    readme = [
        "# EIA-930 hourly demand, the seven US ISOs, 2019 to 2025",
        "",
        "A starter table for Redivis: the hourly electricity demand in the seven US independent system operators' balancing "
        "authorities, from the U.S. Energy Information Administration's Form EIA-930 (the Hourly Electric Grid Monitor), every hour of "
        "2019 to 2025.",
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
        "## Rows, imputed hours, suspect hours and gaps",
        "",
        "Each ISO has 61,368 hours in 2019 to 2025. `demand_mw` is EIA's Adjusted demand: where a balancing authority reported nothing, or a "
        "value EIA found anomalous (EIA's raw Demand column holds, for example, 2,147,480,000 MW in one PJM hour and 0 MW in NYISO hours), EIA "
        "replaced it with its own imputation, and `imputed` is true. The reported value stays in `demand_reported_mw`. An hour with no adjusted "
        "demand at all is left out, never filled by us.",
        "",
        "EIA's adjusted demand still holds a few hours no grid can have: PJM above 170,000 MW in 2020 (PJM's all-time peak is about "
        "166,000 MW), NYISO at 0 MW, CAISO at 14 MW. They are EIA's published values and are kept unchanged; `suspect` is true for them, "
        f"by one stated rule: {SUSPECT_RULE}. Filter `suspect = false` to drop them. The rule is a screen, not EIA's: it can miss a bad "
        "hour that changes slowly, and it may mark a real sudden change.",
        "",
        "| ISO | Balancing authority | Rows | Hours EIA imputed | Hours suspect | Hours left out | Lowest hour, MW | Highest hour, MW | Lowest and highest, not suspect, MW |",
        "|---|---|---|---|---|---|---|---|---|",
        *[f"| {i} | {n} | {r:,} | {k:,} | {su:,} | {m} | {lo:,} | {hi:,} | {olo:,} to {ohi:,} |" for i, n, r, m, lo, hi, k, su, olo, ohi in counts],
        "",
        "## Source",
        "",
        "U.S. Energy Information Administration, Form EIA-930, Hourly Electric Grid Monitor (https://www.eia.gov/electricity/gridmonitor/about): "
        "each balancing authority's workbook, sheet Published Hourly Data, columns Adjusted demand, Demand and Imputed demand. The workbooks used:",
        "",
        *[f"- {ba}: {url} (last modified {lm}; downloaded {got})" for ba, url, lm, got in meta],
        "",
        "Notes: EIA labels each hour by its end; `utc_hour_start` is that label less one hour. EIA's demand is in MWh for the hour, which is "
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
            "It is public domain U.S. government data from EIA's Hourly Electric Grid Monitor, using EIA's own adjusted demand with its imputed "
            "hours and a few implausible hours flagged (never changed), each hour labeled by its start in UTC and local time, and the README "
            "gives the source workbooks and a suggested citation. If the format works for Redivis, the Energy Research Warehouse can supply more tables the same way.\n")
    open(os.path.join(OUT, "note_to_ben.txt"), "w", encoding="utf-8", newline="\n").write(note)
    print(f"wrote {os.path.relpath(OUT, ROOT)}: {len(df):,} rows")


if __name__ == "__main__":
    main()
