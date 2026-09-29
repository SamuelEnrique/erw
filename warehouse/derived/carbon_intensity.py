#!/usr/bin/env python3
"""Carbon intensity per balancing authority, hourly and daily, from EIA-930's CO2 estimates (session 32, Part A2).

Energy Research Warehouse (ERW). Writes two derived series tables (partition column ba), method
docs/methods/emissions.md:

    carbon_intensity_hourly   per BA and hour
    carbon_intensity_daily    per BA and complete UTC day

    intensity_generation  = co2_emissions_generated (eia930_all_emissions, tCO2) x 1000 / net_generation_mw
                            (eia930_all_generation, MWh in the hour), kgCO2/MWh: the CO2 of the power made in the BA
    intensity_demand      = co2_emissions_consumed (eia930_all_emissions, tCO2) x 1000 / demand_mw
                            (eia930_all_demand), kgCO2/MWh: the CO2 of the power used in the BA, imports counted
                            and exports taken out, over its demand

The two differ by trade: a BA that imports power made with more CO2 than its own has a higher demand intensity than
generation intensity, and one that exports its dirtier power the reverse. An hour is written only when its numerator
and a denominator above zero are both in the warehouse; the daily values are energy-weighted (the day's CO2 over the
day's MWh) over UTC days with all 24 hours of both. eia930_all_generation and eia930_all_demand keep about 30 days, so
these tables reach back only that far; the emissions go back to 2018-07-01.

EIA's own intensities in its workbooks (lbs/kWh) divide by positive generation and by "consumed electricity"
(generation by source plus imports minus exports); these divide by the reported net generation and demand, so they
can differ slightly.

    python warehouse/derived/carbon_intensity.py
"""

import datetime as dt
import os
import sys
import traceback

import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.csv as pcsv

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/emissions.md"
EMIS, GEN, DEM = "eia930_all_emissions", "eia930_all_generation", "eia930_all_demand"
COLS = ip.SERIES_COLS + ["ba"]
PAIRS = {"intensity_generation": ("co2_emissions_generated", GEN, "net_generation_mw"),
         "intensity_demand": ("co2_emissions_consumed", DEM, "demand_mw")}


def read(name, variables, since=None):
    """entity, variable, ts_utc, value, geo, ba of a table, streamed and filtered while read."""
    path = os.path.join(ip.OUT_DIR, name + ".csv")
    with open(path, encoding="utf-8") as f:
        n = 0
        for ln in f:
            if not ln.startswith("#"):
                break
            n += 1
    cols = ["entity", "variable", "ts_utc", "value", "geo", "ba"]
    types = {c: pa.string() for c in cols}
    types["value"] = pa.float64()
    reader = pcsv.open_csv(path, read_options=pcsv.ReadOptions(skip_rows=n, block_size=1 << 24),
                           convert_options=pcsv.ConvertOptions(include_columns=cols, column_types=types))
    parts = []
    for b in reader:
        m = pc.is_in(b.column("variable"), value_set=pa.array(variables))
        if since:
            m = pc.and_(m, pc.greater_equal(b.column("ts_utc"), since))
        parts.append(pa.Table.from_batches([b]).filter(m))
    return pa.concat_tables(parts).to_pandas() if parts else pd.DataFrame(columns=cols)


def r4(v):
    from decimal import Decimal, ROUND_HALF_UP
    return float(Decimal(repr(float(v))).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))


def write(df, name, header, log):
    path = os.path.join(ip.OUT_DIR, name + ".csv")
    df = df[COLS].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
    if df.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError(f"{name}: duplicate keys")
    with open(path + ".tmp", "w", encoding="utf-8", newline="") as f:
        for h in header + [f"File holds {len(df)} rows, rewritten whole by this run."]:
            f.write("# " + h + "\n")
        df.to_csv(f, index=False, lineterminator="\n")
    os.replace(path + ".tmp", path)
    log(f"  wrote {name}.csv: {len(df)} rows")
    print(f"{name}.csv: rows={len(df)}")


def main():
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"carbon_intensity_{run_id}.log"))
    results = []
    try:
        gen = read(GEN, ["net_generation_mw"])
        dem = read(DEM, ["demand_mw"])
        since = min(gen["ts_utc"].min(), dem["ts_utc"].min())
        emis = read(EMIS, ["co2_emissions_generated", "co2_emissions_consumed"], since=since)
        log(f"inputs: {EMIS} {len(emis)} rows since {since}; {GEN} {len(gen)}; {DEM} {len(dem)}")
        retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        hourly, daily = [], []
        for var, (co2, table, denom) in PAIRS.items():
            e = emis[emis["variable"] == co2][["entity", "ts_utc", "value", "geo", "ba"]]
            d = (gen if table == GEN else dem)
            d = d[d["variable"] == denom][["entity", "ts_utc", "value"]]
            j = e.merge(d, on=["entity", "ts_utc"], suffixes=("_co2", "_mwh"))
            j = j[j["value_mwh"] > 0]
            j = j.assign(value=(j["value_co2"] * 1000 / j["value_mwh"]).map(r4))
            base = dict(variable=var, unit="kgCO2/MWh", market="", node="", source="erw:carbon_intensity",
                        source_url=METHOD_URL, retrieved_at=retrieved, vintage="")
            hourly.append(j.assign(freq="PT1H", **base)[COLS])
            j = j.assign(day=j["ts_utc"].str[:10])
            g = j.groupby(["entity", "geo", "ba", "day"]).agg(co2=("value_co2", "sum"), mwh=("value_mwh", "sum"),
                                                               n=("value_co2", "size")).reset_index()
            g = g[g["n"] == 24]
            daily.append(pd.DataFrame({"entity": g["entity"], "ts_utc": g["day"] + "T00:00:00Z",
                                       "value": (g["co2"] * 1000 / g["mwh"]).map(r4), "geo": g["geo"], "ba": g["ba"],
                                       "freq": "P1D", **base})[COLS])
            log(f"  {var}: {len(j)} hours, {len(g)} complete days")
        head = lambda what: [  # noqa: E731
            f"Energy Research Warehouse (ERW): carbon intensity per balancing authority, {what} (derived, session 32)",
            "Shape: series (docs/datastandard.md v0), partition column ba, kgCO2/MWh. intensity_generation = EIA's CO2 "
            "emissions generated / net generation; intensity_demand = EIA's CO2 emissions consumed (generated plus "
            "imported minus exported) / demand. Daily values: the day's CO2 over the day's MWh, complete UTC days only.",
            f"Retrieved: {run_id} (UTC) by warehouse/derived/carbon_intensity.py",
            f"Run log: warehouse/output/logs/carbon_intensity_{run_id}.log",
            f"Source: erw:carbon_intensity ERW derived table, emissions method (docs/methods/emissions.md), {METHOD_URL}",
            f"Derived from: {EMIS}; {GEN}; {DEM}",
            f"Reach: the hours eia930_all_generation and eia930_all_demand hold (about 30 days, from {since}).",
        ]
        write(pd.concat(hourly), "carbon_intensity_hourly", head("hourly"), log)
        write(pd.concat(daily), "carbon_intensity_daily", head("daily"), log)
        ip.update_sources([{"source": "erw:carbon_intensity", "publisher": "Energy Research Warehouse (ERW), derived",
                            "report": "Carbon intensity per balancing authority (docs/methods/emissions.md)",
                            "report_url": METHOD_URL, "document_list": "", "license": "public",
                            "tables": ["carbon_intensity_hourly", "carbon_intensity_daily"]}])
        results.append(dict(table="carbon_intensity", market="derived", status="ok", detail="hourly and daily written"))
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"carbon_intensity FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table="carbon_intensity", market="derived", status="failed",
                            detail=tb.strip().splitlines()[-1][:300]))
    ip.write_status("carbon_intensity", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
