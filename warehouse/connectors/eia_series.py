#!/usr/bin/env python3
"""EIA petroleum and natural gas series: products, retail fuels, trade, stocks, LNG exports.

Energy Research Warehouse (ERW) connector, session 7 (docs/price-sources.md,
sections 2, 4 and 8). Reads the full history the EIA API v2 offers for each
series below and writes one `series` table per group. EIA data are public
domain (credit: U.S. Energy Information Administration).

    python warehouse/connectors/eia_series.py            # every table
    python warehouse/connectors/eia_series.py --table eia_lng_exports_monthly

| table                        | route                  | freq    | unit      |
|------------------------------|------------------------|---------|-----------|
| eia_product_spot_prices      | petroleum/pri/spt      | daily   | USD/gal   |
| eia_retail_fuel_prices       | petroleum/pri/gnd      | weekly  | USD/gal   |
| eia_petroleum_trade_weekly   | petroleum/move/wkly    | weekly  | kbbl/d    |
| eia_petroleum_stocks_weekly  | petroleum/stoc/wstk    | weekly  | kbbl      |
| eia_lng_exports_monthly      | natural-gas/move/poe2  | monthly | MMcf, USD/Mcf |

Every series id below was checked against the API on 2026-09-25 (session 7).
Entities are the EIA series ids unchanged (`eia:<series id>`); the header
names each one. Dates follow docs/datastandard.md Decision 11: a daily,
weekly or monthly value sits at 00:00:00Z of the date EIA reports (a weekly
value's date is EIA's week-ending date; a monthly value's is the first day of
the month).

Completeness (Decision 12, trading-day and reporting series): every date EIA
lists must carry a number; a date listed without a value is an omitted
observation and is logged; a table is written only if its newest date is
recent (daily 10 days, weekly 21 days, monthly 150 days: EIA's monthly trade
data lag about three months). A series whose unit is not the expected one
fails the table. Every run replaces each table's full history, so EIA
revisions are picked up. The key comes from EIA_API_KEY.
"""

import argparse
import datetime as dt
import os
import sys
import time
import traceback

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

API = "https://api.eia.gov/v2/"
PAGE = 5000
# EIA unit string -> ERW unit (docs/datastandard.md unit vocabulary)
UNITS = {"$/GAL": "USD/gal", "MBBL/D": "kbbl/d", "MBBL": "kbbl", "MMCF": "MMcf", "$/MCF": "USD/Mcf"}
STALE = {"daily": 10, "weekly": 21, "monthly": 150}
FREQ = {"daily": "P1D", "weekly": "P1W", "monthly": "P1M"}
LNG_TERMINALS = ["SPL", "CRP", "CAM", "FPT", "CCPL", "PLAQ", "CPT", "ELBA", "GPT"]

TABLES = {
    "eia_product_spot_prices": dict(
        route="petroleum/pri/spt", freq="daily", geo="US",
        title="EIA refined product spot prices: gasoline, RBOB, ULSD, CARB diesel, jet fuel, heating oil, propane",
        report="Spot Prices for Crude Oil and Petroleum Products",
        page="https://www.eia.gov/dnav/pet/pet_pri_spt_s1_d.htm",
        variable=lambda unit: "spot_price",
        series=["EER_EPMRU_PF4_Y35NY_DPG", "EER_EPMRU_PF4_RGC_DPG", "EER_EPMRR_PF4_Y05LA_DPG",
                "EER_EPD2DXL0_PF4_Y35NY_DPG", "EER_EPD2DXL0_PF4_RGC_DPG", "EER_EPD2DC_PF4_Y05LA_DPG",
                "EER_EPJK_PF4_RGC_DPG", "EER_EPD2F_PF4_Y35NY_DPG", "EER_EPLLPA_PF4_Y44MB_DPG"]),
    "eia_retail_fuel_prices": dict(
        route="petroleum/pri/gnd", freq="weekly", geo="US",
        title="EIA US retail gasoline and diesel prices, weekly",
        report="Gasoline and Diesel Fuel Update (retail prices)",
        page="https://www.eia.gov/dnav/pet/pet_pri_gnd_dcus_nus_w.htm",
        variable=lambda unit: "retail_price",
        series=["EMM_EPMR_PTE_NUS_DPG", "EMM_EPM0_PTE_NUS_DPG", "EMD_EPD2D_PTE_NUS_DPG"]),
    "eia_petroleum_trade_weekly": dict(
        route="petroleum/move/wkly", freq="weekly", geo="US",
        title="EIA US crude oil and petroleum product imports and exports, weekly",
        report="Weekly Petroleum Status Report: imports and exports",
        page="https://www.eia.gov/petroleum/supply/weekly/",
        variable=lambda unit: "flow",
        series=["WCREXUS2", "WRPEXUS2", "WTTEXUS2", "WCRIMUS2", "WRPIMUS2", "WTTIMUS2", "WCRNTUS2"]),
    "eia_petroleum_stocks_weekly": dict(
        route="petroleum/stoc/wstk", freq="weekly", geo="US",
        title="EIA US crude oil and petroleum product ending stocks, weekly",
        report="Weekly Petroleum Status Report: stocks",
        page="https://www.eia.gov/petroleum/supply/weekly/",
        variable=lambda unit: "stocks",
        series=["WCESTUS1", "WCSSTUS1", "WCRSTUS1", "WGTSTUS1", "WDISTUS1", "WKJSTUS1",
                "WPRSTUS1", "WTTSTUS1"]),
    "eia_lng_exports_monthly": dict(
        route="natural-gas/move/poe2", freq="monthly", geo="US",
        title="EIA US LNG exports by terminal: volume and price, monthly",
        report="U.S. Natural Gas Exports and Re-Exports by Point of Exit (LNG)",
        page="https://www.eia.gov/dnav/ng/ng_move_poe2_a_EPG0_ENG_Mmcf_m.htm",
        variable=lambda unit: "export_volume" if unit == "MMcf" else "export_price",
        series=[f"NGM_EPG0_ENG_Y{t}-Z00_MMCF" for t in LNG_TERMINALS]
        + [f"NGM_EPG0_PNG_Y{t}-Z00_DMCF" for t in LNG_TERMINALS]),
}


def fetch(route, freq, sids, key, log):
    """All rows for these series ids, paged; each row keeps its page URL (key removed)."""
    out, offset = [], 0
    while True:
        params = [("api_key", key), ("frequency", freq), ("data[0]", "value"),
                  ("sort[0][column]", "period"), ("sort[0][direction]", "asc"),
                  ("sort[1][column]", "series"), ("sort[1][direction]", "asc"),
                  ("offset", str(offset)), ("length", str(PAGE))]
        params += [("facets[series][]", s) for s in sids]

        def call():
            r = requests.get(API + route + "/data/", params=params, timeout=120)
            if r.status_code != 200:
                raise RuntimeError(f"EIA {route} HTTP {r.status_code}: {ip.redact(r.text[:300])}")
            return r
        r = ip.with_retries(f"EIA {route} offset {offset}", call, log)
        body = r.json()["response"]
        rows = body.get("data", [])
        total = int(body.get("total", 0))
        url, got = ip.redact(r.url), ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        for row in rows:
            row["_url"], row["_retrieved"] = url, got
        out += rows
        log(f"  {route} offset {offset}: {len(rows)} rows (total {total})")
        offset += len(rows)
        if not rows or offset >= total:
            break
        time.sleep(0.5)
    if len(out) != total:
        raise RuntimeError(f"EIA {route}: got {len(out)} rows, API reported {total}")
    return pd.DataFrame(out)


def ts_of(period, freq):
    if freq == "monthly":
        return pd.to_datetime(period, format="%Y-%m").dt.strftime("%Y-%m-01T00:00:00Z")
    return pd.to_datetime(period, format="%Y-%m-%d").dt.strftime("%Y-%m-%dT00:00:00Z")


def build(name, cfg, key, run_id, log):
    log(f"{name} ({cfg['route']}, {cfg['freq']}, {len(cfg['series'])} series):")
    df = fetch(cfg["route"], cfg["freq"], cfg["series"], key, log)
    missing = sorted(set(cfg["series"]) - set(df["series"]))
    if missing:
        raise RuntimeError(f"{name}: EIA returned nothing for {missing}")
    bad_units = sorted(set(df["units"]) - set(UNITS))
    if bad_units:
        raise RuntimeError(f"{name}: unexpected EIA units {bad_units}")
    if df.duplicated(["series", "period"]).any():
        raise RuntimeError(f"{name}: EIA lists a (series, period) more than once")
    value = pd.to_numeric(df["value"], errors="coerce")
    text = df["value"].astype(str).str.strip()
    nonnum = df[value.isna() & df["value"].notna() & (text != "") & (text.str.lower() != "none")]
    if len(nonnum):
        raise RuntimeError(f"{name}: non-numeric values {nonnum['value'].unique()[:5]}")
    empty = df[value.isna()]
    if len(empty):
        by = empty.groupby("series").size().to_dict()
        log(f"  dates EIA lists without a value (omitted): {by}")
    keep = value.notna()
    d = df[keep].copy()
    d["unit"] = d["units"].map(UNITS)
    s = pd.DataFrame({
        "entity": "eia:" + d["series"],
        "variable": d["unit"].map(cfg["variable"]),
        "ts_utc": ts_of(d["period"], cfg["freq"]).values,
        "value": value[keep].values,
        "unit": d["unit"].values,
        "freq": FREQ[cfg["freq"]],
        "geo": cfg["geo"],
        "market": "", "node": "",
        "source": f"eia:{cfg['route']}",
        "source_url": d["_url"].values,
        "retrieved_at": d["_retrieved"].values,
        "vintage": "",
    }).sort_values(["entity", "variable", "ts_utc"])
    newest = pd.Timestamp(s["ts_utc"].max()[:10])
    age = (pd.Timestamp.now(tz="UTC").tz_localize(None).normalize() - newest).days
    if age > STALE[cfg["freq"]]:
        raise RuntimeError(f"{name}: newest date {newest.date()} is {age} days old (limit "
                           f"{STALE[cfg['freq']]}); not writing a stale table")
    names = df.drop_duplicates("series").set_index("series")["series-description"].to_dict()
    header = [
        f"Energy Research Warehouse (ERW): {cfg['title']}",
        f"Shape: series (docs/datastandard.md v0). freq {FREQ[cfg['freq']]}: ts_utc is the date EIA "
        "reports at 00:00:00Z (weekly: week-ending date; monthly: first of the month).",
        "Window: the full history the EIA API v2 offers; every run replaces all of it.",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_series.py via the EIA API v2",
        f"Run log: warehouse/output/logs/eia_series_{run_id}.log (every API request, key removed)",
        f"Raw files: warehouse/raw/eia_series/{run_id}/ (not in git; manifest.csv lists each file and URL)",
        f"Source: eia:{cfg['route']} {cfg['report']}, {cfg['page']}",
        f"  document list: {API}{cfg['route']}/",
        "Series: " + "; ".join(f"{k} = {names.get(k, '')}" for k in cfg["series"]),
        f"Dates EIA lists without a value, omitted: {int(len(empty))}. License: public domain (EIA).",
    ]
    ip.write_csv(s[ip.SERIES_COLS], name, header, log)
    ip.update_sources([dict(source=f"eia:{cfg['route']}",
                            publisher="U.S. Energy Information Administration (EIA)",
                            report=cfg["report"], report_url=cfg["page"],
                            document_list=f"{API}{cfg['route']}/", tables=[name])])


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW EIA petroleum and gas series")
    ap.add_argument("--table", action="append", choices=sorted(TABLES))
    ap.add_argument("--out-dir")
    args = ap.parse_args(argv)
    if args.out_dir:
        ip.set_out_dir(args.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"eia_series_{run_id}.log"))
    ip.RAW.open("eia_series", run_id)
    key = ip.load_key("EIA_API_KEY", log)
    results = []
    for name in args.table or sorted(TABLES):
        try:
            if key is None:
                raise RuntimeError("EIA_API_KEY is empty")
            build(name, TABLES[name], key, run_id, log)
            results.append(dict(table=name, market=TABLES[name]["freq"], status="ok", detail=""))
        except Exception:
            tb = ip.redact(traceback.format_exc())
            last = tb.strip().splitlines()[-1]
            log(f"{name} FAILED, no output file written:\n{tb}")
            print(f"eia_series {name} FAILED, no output file written: {last}", file=sys.stderr)
            results.append(dict(table=name, market=TABLES[name]["freq"], status="failed", detail=last[:300]))
    ip.write_status("eia_series", run_id, results)
    failures = sum(r["status"] != "ok" for r in results)
    log(f"done, failures={failures}")
    log.close()
    print(f"eia_series run log: {os.path.relpath(log.path, ip.ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
