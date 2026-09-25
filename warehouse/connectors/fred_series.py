#!/usr/bin/env python3
"""FRED series without a key: public-domain spot prices and IMF monthly commodity prices.

Energy Research Warehouse (ERW) connector, session 7 (docs/price-sources.md,
sections 2, 3, 5 and 6). FRED's graph CSV route needs no key:
https://fred.stlouisfed.org/graph/fredgraph.csv?id=<ID>. Two `series` tables:

| table                     | series | freq | license |
|---------------------------|--------|------|---------|
| fred_daily_spot_prices    | DCOILWTICO, DCOILBRENTEU, DHHNGSP (EIA data on FRED) | P1D | public (FRED "Public Domain: Citation Requested") |
| fred_imf_commodity_prices | PNGASEUUSDM (EU gas, the TTF proxy), PNGASJPUSDM (Asia LNG, a JKM proxy, not JKM), PCOALAUUSDM (Australian coal), PURANUSDM (uranium), PNICKUSDM (nickel) | P1M | internal (FRED "Copyrighted: Citation Required"; IMF data, non-personal use needs the owner's permission) |

    python warehouse/connectors/fred_series.py [--table fred_daily_spot_prices]

Entities are `fred:<series id>`. Each run reads every series' FRED page and
checks its units and its copyright line against the table below; a change in
either fails the table, so a series cannot drift into the wrong license or
unit silently. FRED writes "." (or nothing) for a date without a value; such a
date is omitted and counted in the log. Freshness: a daily table's newest date
must be within 10 days, a monthly one's within 150 days.

Note: FRED's servers stalled (no response in 60 s) for requests sent with a
browser User-Agent on 2026-09-25 and answered at once with the requests default
one, so this connector sends requests' default headers.
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

CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={}"
PAGE = "https://fred.stlouisfed.org/series/{}"
PD, CR = "Public Domain: Citation Requested", "Copyrighted: Citation Required"
# FRED "Units:" text -> ERW unit
UNITS = {"Dollars per Barrel": "USD/bbl", "Dollars per Million BTU": "USD/MMBtu",
         "U.S. Dollars per Million Metric British Thermal Unit": "USD/MMBtu",
         "U.S. Dollars per Metric Ton": "USD/t", "U.S. Dollars per Pound": "USD/lb"}

TABLES = {
    "fred_daily_spot_prices": dict(
        freq="P1D", stale=10, rights=PD, license="public", variable="spot_price",
        title="FRED daily spot prices: WTI, Brent, Henry Hub (EIA data, public domain)",
        series={"DCOILWTICO": "USD/bbl", "DCOILBRENTEU": "USD/bbl", "DHHNGSP": "USD/MMBtu"}),
    "fred_imf_commodity_prices": dict(
        freq="P1M", stale=150, rights=CR, license="internal", variable="price",
        title="FRED IMF global commodity prices, monthly: EU gas, Asia LNG, Australian coal, uranium, nickel",
        series={"PNGASEUUSDM": "USD/MMBtu", "PNGASJPUSDM": "USD/MMBtu", "PCOALAUUSDM": "USD/t",
                "PURANUSDM": "USD/lb", "PNICKUSDM": "USD/t"}),
}


def get(url, what, log):
    def call():
        r = requests.get(url, timeout=90)
        if r.status_code != 200:
            raise RuntimeError(f"{what} HTTP {r.status_code}")
        return r
    return ip.with_retries(what, call, log)


def meta(sid, log):
    """(title, ERW unit, copyright line) from the series page."""
    t = get(PAGE.format(sid), f"FRED page {sid}", log).text
    title = re.sub(r"\s+", " ", re.search(r"<title>(.*?)</title>", t, re.S).group(1)).split(" | ")[0].strip()
    m = re.search(r'class="series-meta-value-units">([^<]+)<', t)
    if not m:
        raise RuntimeError(f"FRED {sid}: no Units line on the series page")
    unit_text = re.sub(r"\s+", " ", m.group(1)).strip()
    if unit_text not in UNITS:
        raise RuntimeError(f"FRED {sid}: unknown units {unit_text!r}")
    rights = [r for r in (PD, CR) if r in t]
    if len(rights) != 1:
        raise RuntimeError(f"FRED {sid}: copyright line not found or ambiguous: {rights}")
    return title, UNITS[unit_text], rights[0]


def build(name, cfg, run_id, log):
    frames, names, omitted = [], {}, {}
    for sid, unit in cfg["series"].items():
        title, got_unit, rights = meta(sid, log)
        if got_unit != unit:
            raise RuntimeError(f"FRED {sid}: units are {got_unit}, expected {unit}")
        if rights != cfg["rights"]:
            raise RuntimeError(f"FRED {sid}: page says {rights!r}, table expects {cfg['rights']!r}")
        names[sid] = title
        url = CSV.format(sid)
        r = get(url, f"FRED CSV {sid}", log)
        got = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        d = pd.read_csv(io.StringIO(r.text), dtype=str, keep_default_na=False)
        if list(d.columns) != ["observation_date", sid]:
            raise RuntimeError(f"FRED {sid}: CSV columns {list(d.columns)}")
        v = d[sid].str.strip()
        miss = v.isin(["", "."])
        bad = v[~miss & pd.to_numeric(v, errors="coerce").isna()]
        if len(bad):
            raise RuntimeError(f"FRED {sid}: non-numeric values {bad.unique()[:5]}")
        omitted[sid] = int(miss.sum())
        d = d[~miss]
        if not d["observation_date"].str.fullmatch(r"\d{4}-\d{2}-\d{2}").all():
            raise RuntimeError(f"FRED {sid}: a date is not YYYY-MM-DD")
        frames.append(pd.DataFrame({
            "entity": f"fred:{sid}", "variable": cfg["variable"],
            "ts_utc": d["observation_date"] + "T00:00:00Z", "value": pd.to_numeric(d[sid]).round(6),
            "unit": unit, "freq": cfg["freq"], "geo": "", "market": "", "node": "",
            "source": f"fred:{sid}", "source_url": url, "retrieved_at": got, "vintage": ""}))
        log(f"  {sid}: {len(d)} values, {d['observation_date'].min()} to {d['observation_date'].max()}, "
            f"{omitted[sid]} dates without a value omitted; {unit}; {rights}")
    s = pd.concat(frames, ignore_index=True).sort_values(["entity", "ts_utc"])
    for sid, g in s.groupby("entity"):
        newest = pd.Timestamp(g["ts_utc"].max()[:10])
        age = (pd.Timestamp.now(tz="UTC").tz_localize(None).normalize() - newest).days
        if age > cfg["stale"]:
            raise RuntimeError(f"{name}: {sid} newest date {newest.date()} is {age} days old; not writing")
    header = [
        f"Energy Research Warehouse (ERW): {cfg['title']}",
        f"Shape: series (docs/datastandard.md v0). freq {cfg['freq']}: ts_utc is FRED's observation "
        "date at 00:00:00Z (monthly: first of the month).",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/fred_series.py (FRED graph CSV, no key)",
        f"Run log: warehouse/output/logs/fred_series_{run_id}.log",
        f"Raw files: warehouse/raw/fred_series/{run_id}/ (not in git)",
        "Source: Federal Reserve Bank of St. Louis, FRED, https://fred.stlouisfed.org/ ; series: "
        + "; ".join(f"{k} = {names[k]}" for k in cfg["series"]),
        f"FRED rights line on every series page: {cfg['rights']}. Dates without a value omitted: "
        f"{sum(omitted.values())}.",
        f"License: {cfg['license']}."
        + (" IMF data on FRED; non-personal use needs the owner's permission." if cfg["license"] == "internal" else ""),
    ]
    ip.write_csv(s[ip.SERIES_COLS], name, header, log)
    ip.update_sources([dict(source=f"fred:{sid}", publisher="Federal Reserve Bank of St. Louis (FRED)",
                            report=f"{names[sid]} ({cfg['rights']})", report_url=PAGE.format(sid),
                            document_list=CSV.format(sid), license=cfg["license"], tables=[name])
                       for sid in cfg["series"]])


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW FRED series, no key")
    ap.add_argument("--table", action="append", choices=sorted(TABLES))
    args = ap.parse_args(argv)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"fred_series_{run_id}.log"))
    ip.RAW.open("fred_series", run_id)
    results = []
    for name in args.table or sorted(TABLES):
        try:
            log(f"{name}:")
            build(name, TABLES[name], run_id, log)
            results.append(dict(table=name, market=TABLES[name]["freq"], status="ok", detail=""))
        except Exception:
            tb = ip.redact(traceback.format_exc())
            last = tb.strip().splitlines()[-1]
            log(f"{name} FAILED, no output file written:\n{tb}")
            print(f"fred_series {name} FAILED, no output file written: {last}", file=sys.stderr)
            results.append(dict(table=name, market=TABLES[name]["freq"], status="failed", detail=last[:300]))
    ip.write_status("fred_series", run_id, results)
    failures = sum(r["status"] != "ok" for r in results)
    log(f"done, failures={failures}")
    log.close()
    print(f"fred_series run log: {os.path.relpath(log.path, ip.ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
