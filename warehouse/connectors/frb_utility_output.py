#!/usr/bin/env python3
"""The Federal Reserve's industrial production and capacity utilization of electric and gas utilities, a month (session
889, chain 048: the output of the power sector by kind of sale and by fuel, as the Federal Reserve measures it).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/frb_utility_output_monthly.csv, from the
Board of Governors of the Federal Reserve System's G.17 release (Industrial Production and Capacity Utilization), its
whole-release text files:

    https://www.federalreserve.gov/releases/g17/ipdisk/ip_sa.txt     industrial production, seasonally adjusted
    https://www.federalreserve.gov/releases/g17/ipdisk/utl_sa.txt    capacity utilization, seasonally adjusted

    entity    frb_g17:<G.17 series code>: the utilities (NAICS 2211 and 2212: G2211A2 electric and gas utilities, G2211
              electric power, G22111 generation, N221112 fossil fuel, N221113 nuclear, G221111A4T8 hydroelectric,
              renewables and other, with its parts N221111 hydroelectric and N221114T8 renewables and other, G22112
              transmission and distribution, N22112R, N22112C, N22112M residential, commercial and other, and
              industrial electricity sales, G2212 natural gas distribution, N2212R, N2212C, N2212M its residential,
              commercial and other, and industrial sales, N2212T gas transmission), and for comparison B50001 (all
              industrial production) and B50089 (energy, total); the detailed N series can end a few months before
              the aggregates
    variable  production (unit index: the G.17 release's base, 2017 = 100; Decision 53) or utilization (pct of capacity)
    ts_utc    the month's first day; freq P1M; geo US; node the series' title as the file gives it

A month the file leaves empty has no row; nothing is filled. A file whose lines are not in the form read stops the run;
so does a key given twice. Each release revises earlier months: the table is a snapshot of the release read.

    python warehouse/connectors/frb_utility_output.py [--offline]

Ceiling: two requests (the two files; saved in warehouse/raw/frb_utility_output/ and reused offline). The host has no
robots file (HTTP 404, session 889). License: "Unless otherwise indicated, information on Board's website is in the
public domain and may be copied and distributed without permission. Please cite to the Board as the source of the
information." (license_reads.csv, read 41).
"""

import argparse
import datetime as dt
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "frb_utility_output_monthly"
CONNECTOR = "frb_utility_output"
SOURCE = "frb:g17"
RELEASE = "https://www.federalreserve.gov/releases/g17/"
FILES = {"production": ("https://www.federalreserve.gov/releases/g17/ipdisk/ip_sa.txt", "index"),
         "utilization": ("https://www.federalreserve.gov/releases/g17/ipdisk/utl_sa.txt", "pct")}
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ERW data machine; Energy Research Warehouse, github.com/SamuelEnrique/erw)"}
TITLE_RE = re.compile(r'^"([A-Z0-9@]+): (.*)"\s*$')
DATA_RE = re.compile(r'^"([A-Z0-9@]+)"\s+(\d{4})((?:\s+-?[\d.]+)*)\s*$')


def wanted(code):
    """The utilities' series (NAICS 2211 and 2212), and the two totals for comparison."""
    return bool(re.match(r"^[GN]221", code)) or code in ("B50001", "B50089")


def parse(text, variable, unit, url, retrieved):
    titles, out = {}, []
    for ln in text.splitlines():
        if not ln.strip():
            continue
        m = TITLE_RE.match(ln)
        if m:
            titles[m.group(1)] = re.sub(r"\s+", " ", m.group(2)).strip()
            continue
        m = DATA_RE.match(ln)
        if not m:
            raise RuntimeError(f"a line not in the form read: {ln[:80]!r}")
        code, year, vals = m.group(1), int(m.group(2)), m.group(3).split()
        if not wanted(code):
            continue
        if len(vals) > 12:
            raise RuntimeError(f"{code} {year}: {len(vals)} months")
        for i, v in enumerate(vals):
            out.append(dict(entity=f"frb_g17:{code}", variable=variable, ts_utc=f"{year}-{i + 1:02d}-01T00:00:00Z", value=float(v),
                            unit=unit, freq="P1M", geo="US", market="", node=titles.get(code, code), source=SOURCE,
                            source_url=url, retrieved_at=retrieved, vintage=""))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an (entity, variable, ts_utc) is given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="The Federal Reserve's G.17: utilities' output and capacity utilization")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        frames, got = [], []
        for variable, (url, unit) in FILES.items():
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline, headers=HEADERS)
            frames.append(parse(content.decode("utf-8", errors="replace"), variable, unit, url, rec.get("retrieved_at") or ""))
            got.append(f"{url} (retrieved {rec.get('retrieved_at', '')})")
        s = pd.concat(frames, ignore_index=True)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a row in both files")
        s = s[ip.SERIES_COLS].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        last = s["ts_utc"].max()[:7]
        ends = s.groupby("entity")["ts_utc"].max().str[:7]
        last_by = "; ".join(f"{m}: {', '.join(sorted(e.split(':')[1] for e in ends.index[ends == m]))}" for m in sorted(ends.unique(), reverse=True))
        header = [
            "Energy Research Warehouse (ERW): the Federal Reserve's G.17, industrial production and capacity utilization of electric and gas utilities, a month (session 889)",
            "Shape: series (docs/datastandard.md v0). entity frb_g17:<G.17 series code>; variable production (unit index, the G.17 release's base 2017 = 100; "
            "Decision 53) or utilization (pct of capacity); seasonally adjusted; ts_utc the month's first day; freq P1M; geo US; node the series' title. "
            "Codes: G2211A2 electric and gas utilities; G2211 electric power; G22111 generation (N221112 fossil fuel, N221113 nuclear, G221111A4T8 "
            "hydroelectric, renewables and other, with N221111 hydroelectric and N221114T8 renewables and other); G22112 transmission and distribution "
            "(N22112R residential, N22112C commercial and other, N22112M industrial electricity sales); G2212 natural gas distribution (N2212R, N2212C, "
            "N2212M its residential, commercial and other, and industrial sales; N2212T gas transmission); B50001 all industrial production and B50089 "
            "energy, total, for comparison.",
            f"Months to {last} (each series' last month: {last_by}); {s['entity'].nunique()} series, {len(s):,} rows. A month the file leaves empty has no row; "
            "nothing is filled. An index is never summed. "
            "Each release revises earlier months: this is the release read.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/frb_utility_output.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Board of Governors of the Federal Reserve System, G.17 Industrial Production and Capacity Utilization, {RELEASE}",
            f"  access: {'; '.join(got)}",
            "License: public (the Board: \"Unless otherwise indicated, information on Board's website is in the public domain and may be copied and "
            "distributed without permission. Please cite to the Board as the source of the information.\").",
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Board of Governors of the Federal Reserve System",
                                    report="G.17 Industrial Production and Capacity Utilization", report_url=RELEASE,
                                    document_list=RELEASE, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(s):,} rows"))
        print(f"{NAME}: {len(s):,} rows, {s['entity'].nunique()} series, months to {last}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"{CONNECTOR} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
