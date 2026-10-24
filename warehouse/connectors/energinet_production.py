#!/usr/bin/env python3
"""Denmark's electricity an hour, by price area: production by technology, gross consumption and the exchanges with
each neighbour, from Energinet's Energi Data Service (session 2217, chain 098: a wind-led grid beside the U.S. ones, a
second source of the session's own choosing).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/energinet_dk_production_hourly.csv, from
the open API's dataset ProductionConsumptionSettlement (settlement data from DataHub, no key), one request:

    https://api.energidataservice.dk/dataset/ProductionConsumptionSettlement?start=<from>&end=<to>&limit=0&sort=HourUTC%20ASC

The answer is JSON, one record an hour and price area (DK1 west of the Great Belt, DK2 east), each measure in MWh for
the hour. Twenty-one are taken:

    production    central_power, local_power, commercial_power, commercial_power_self_con, offshore_wind_lt100mw,
                  offshore_wind_ge100mw, onshore_wind_lt50kw, onshore_wind_ge50kw, hydro_power, solar_power_lt10kw,
                  solar_power_ge10lt40kw, solar_power_ge40kw, solar_power_self_con, unknown_prod
    consumption   gross_consumption (Energinet: "Calculated as sum of all production including self-consumption plus
                  sum of exchange", so it includes the transmission and distribution grid losses but not the
                  interconnectors' losses, which Energinet says are "Not included in the Gross consumption")
    exchanges     exchange_no, exchange_se, exchange_ge, exchange_nl, exchange_gb, exchange_great_belt (negative an
                  export, positive an import, as Energinet signs them)

Not taken: the three grid losses and power-to-heat (the last inside gross consumption). commercial_power_self_con is
Energinet's column LocalPowerSelfConMWh, whose display name is "Commercial power self-consumption (terminated)" ("Named
before commercial power was separated from Local power, therefor the confusing DB name"); Energinet calls it "Very
uncertain", says it overlaps solar self-consumption and should be excluded from total consumption, and ended it from
1 September 2026 (null since, so no row). It is taken because gross consumption counts it until then (session 2218).

A break at 1 September 2026: Energinet's caution says the dataset "has changed as part of the transition to DataHub
3.0 ... the values will be calculated using a different method"; local_power steps up from that day (DK1's monthly
mean 80.83 MWh in August 2026, 122.84 in September; session 2218's note) as the self-consumption column ends.

    entity      energinet:<price area> (DK1, DK2); node the price area
    unit        MWh; ts_utc HourUTC, the hour's start in UTC; freq PT1H; geo DK
    x_*         the hour in Danish time (HourDK)

Energinet updates settlement data for up to two years ("normally 99% correct after 15 days ... 99,9% correct" after
three months, its comment). Values as published; a null has no row; nothing is filled. A record without the fields
named here, a value that is not a number or an hour and area given twice stops the run.

    python warehouse/connectors/energinet_production.py [--start 2025-01-01] [--end 2026-10-15] [--offline] [--out-dir DIR]

Ceiling: one request, reused from warehouse/raw/energinet_production/ with --offline. Neither api.energidataservice.dk
nor www.energidataservice.dk has a robots file (session 2215). License: CC BY 4.0 (Energinet's Terms and Conditions,
session 2215): "Source: Energinet (www.energidataservice.dk)"; the rows are reshaped from wide to long, not changed.
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "energinet_dk_production_hourly"
CONNECTOR = "energinet_production"
SOURCE = "energinet:production_consumption_settlement"
PAGE = "https://www.energidataservice.dk/tso-electricity/ProductionConsumptionSettlement"
API = "https://api.energidataservice.dk/dataset/ProductionConsumptionSettlement?start={a}T00:00&end={b}T00:00&limit=0&sort=HourUTC%20ASC"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
FIELDS = {"CentralPowerMWh": "central_power", "LocalPowerMWh": "local_power", "LocalPowerSelfConMWh": "commercial_power_self_con",
          "CommercialPowerMWh": "commercial_power",
          "OffshoreWindLt100MW_MWh": "offshore_wind_lt100mw", "OffshoreWindGe100MW_MWh": "offshore_wind_ge100mw",
          "OnshoreWindLt50kW_MWh": "onshore_wind_lt50kw", "OnshoreWindGe50kW_MWh": "onshore_wind_ge50kw",
          "HydroPowerMWh": "hydro_power", "SolarPowerLt10kW_MWh": "solar_power_lt10kw",
          "SolarPowerGe10Lt40kW_MWh": "solar_power_ge10lt40kw", "SolarPowerGe40kW_MWh": "solar_power_ge40kw",
          "SolarPowerSelfConMWh": "solar_power_self_con", "UnknownProdMWh": "unknown_prod",
          "GrossConsumptionMWh": "gross_consumption", "ExchangeNO_MWh": "exchange_no", "ExchangeSE_MWh": "exchange_se",
          "ExchangeGE_MWh": "exchange_ge", "ExchangeNL_MWh": "exchange_nl", "ExchangeGB_MWh": "exchange_gb",
          "ExchangeGreatBelt_MWh": "exchange_great_belt"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_hour_dk"]
STAMP = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")


def build(body, url, retrieved, vintage):
    d = json.loads(body)
    recs = d.get("records")
    if not isinstance(recs, list) or d.get("dataset") != "ProductionConsumptionSettlement":
        raise RuntimeError("the answer is not the dataset's records")
    out = []
    for r in recs:
        missing = [k for k in ["HourUTC", "HourDK", "PriceArea", *FIELDS] if k not in r]
        if missing:
            raise RuntimeError(f"a record without {missing[:3]}")
        hour, area = str(r["HourUTC"]), str(r["PriceArea"]).strip()
        if not STAMP.fullmatch(hour):
            raise RuntimeError(f"an hour not in Energinet's form: {hour!r}")
        for k, var in FIELDS.items():
            v = r[k]
            if v is None:
                continue
            if not isinstance(v, (int, float)):
                raise RuntimeError(f"{area} {hour} {k}: not a number: {v!r}")
            out.append({"entity": f"energinet:{area}", "variable": var, "ts_utc": hour + "Z", "value": float(v), "unit": "MWh",
                        "freq": "PT1H", "geo": "DK", "market": "", "node": area, "source": SOURCE, "source_url": url,
                        "retrieved_at": retrieved, "vintage": vintage, "x_hour_dk": str(r["HourDK"])})
    t = pd.DataFrame(out, columns=COLS)
    twice = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"an hour given twice: {twice.entity.iloc[0]} {twice.variable.iloc[0]} {twice.ts_utc.iloc[0]}")
    return t.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True), int(d.get("total") or 0)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Energinet: Denmark's production, consumption and exchanges an hour, by price area")
    ap.add_argument("--start", default="2025-01-01")
    ap.add_argument("--end", default="2026-10-15")
    ap.add_argument("--offline", action="store_true", help="the saved answer only, no request")
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
        if not args.offline and (ip.paused("energinet") or ip.paused_host("api.energidataservice.dk")):
            raise RuntimeError("Energinet is paused (warehouse/metadata/paused_sources.csv): not requested")
        url = API.format(a=args.start, b=args.end)
        content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=300)
        t, total = build(content.decode("utf-8", errors="replace"), url, rec.get("retrieved_at") or "", ip.vintage_of(rec))
        hours = t.groupby("entity").ts_utc.agg(["min", "max", "nunique"])
        header = [
            f"Energy Research Warehouse (ERW): Energinet, Energi Data Service, ProductionConsumptionSettlement: Denmark's production by technology, gross consumption and exchanges an hour, by price area, {t.ts_utc.min()[:10]} to {t.ts_utc.max()[:10]} (session 2217)",
            "Shape: series (docs/datastandard.md v0). entity energinet:<price area> (DK1, DK2); variable the measure in snake case (central_power ... exchange_great_belt; exchanges negative for export); unit MWh for the hour; "
            "ts_utc the hour's start in UTC; freq PT1H; geo DK. Settlement data, revised for up to two years (Energinet).",
            f"{len(t)} rows from {total} of Energinet's records: " + "; ".join(f"{e} {int(r['nunique'])} hours" for e, r in hours.iterrows())
            + ". Grid losses and power-to-heat are not taken. Gross consumption is Energinet's sum of production and exchange (the interconnectors' losses outside it); commercial_power_self_con (Energinet's LocalPowerSelfConMWh, 'very uncertain') ends 1 September 2026, where Energinet's DataHub 3.0 method change begins and local_power steps up. A null has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/energinet_production.py; the answer retrieved {rec.get('retrieved_at') or ''}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Energinet, Energi Data Service, Production and Consumption - Settlement, {PAGE}",
            f"  access: {url}",
            "License: public, CC BY 4.0. Source: Energinet (www.energidataservice.dk). The records are reshaped from wide to long; no value is changed.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Energinet (Energi Data Service)",
                                    report="Energi Data Service, Production and Consumption - Settlement (ProductionConsumptionSettlement)",
                                    report_url=PAGE, document_list=API.format(a="<from>", b="<to>"), license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows from {total} records")
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
