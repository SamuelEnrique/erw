#!/usr/bin/env python3
"""Historical Event Analyzer v0 (session 36B): one derived table of daily figures around an event and the same calendar
days of earlier years, the baseline. The first event is Winter Storm Uri in ERCOT, February 2021.

Energy Research Warehouse (ERW). Writes warehouse/output/event_window_daily.csv, a series table with the partition
columns ba and event (docs/datastandard.md decision 31), rewritten whole each run. Method: docs/methods/events.md.

Days are ERCOT operating days (America/Chicago), labelled with the local date at 00:00:00Z (decision 11). A day's value
is written only when every interval of that day is present (96 real-time, 24 day-ahead or 24 EIA-930 hours); nothing
is filled. Variables per day:

    entity ercot:HB_HUBAVG (ercot_all_hub_prices_history, ERCOT's own settlement point prices)
        rt_mean, rt_max        the day's mean and highest 15-minute real-time price, USD/MWh (market ercot_rtm)
        da_mean, da_max        the day's mean and highest hourly day-ahead price, USD/MWh (market ercot_dam)
    entity eia930:ERCO (EIA's per-BA workbook, sheet Published Hourly Data, from the emissions connector's extract;
    CO2 from eia930_all_emissions)
        demand_mwh             the day's demand served, MWh (the sum of 24 hourly values)
        demand_min_mw          the day's lowest hour of demand, MW
        demand_max_mw          the day's highest hour of demand, MW
        net_generation_mwh     the day's net generation, MWh
        intensity_generation   CO2 generated / net generation over the day, kgCO2/MWh (as carbon_intensity_daily,
                               but over the local day)
    event days only:
        demand_mwh_vs_baseline, net_generation_mwh_vs_baseline   the event day minus the mean of the baseline years'
                               same calendar day, MWh
        demand_mwh_day_change, net_generation_mwh_day_change     the event day minus the previous day of the window, MWh

Demand during rotating outages is load that was served, not what customers wanted: the power cut off is not in it.

    python warehouse/derived/event_window.py
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
import eia930_emissions as em  # noqa: E402  (latest_extract, read_extract, extract_meta)
import iso_prices as ip  # noqa: E402

NAME = "event_window_daily"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/events.md"
PRICES, EMIS = "ercot_all_hub_prices_history", "eia930_all_emissions"
COLS = ip.SERIES_COLS + ["ba", "event"]
EVENTS = [
    # event id, BA code, time zone, hub entity, window start and end (inclusive, local dates), baseline years
    dict(event="uri_2021", ba="erco", entity="eia930:ERCO", tz="America/Chicago", hub="ercot:HB_HUBAVG",
         start="2021-02-07", end="2021-02-24", baseline=[2019, 2020]),
]


def r4(v):
    from decimal import Decimal, ROUND_HALF_UP
    return float(Decimal(repr(float(v))).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))


def stream(name, keep, cols):
    """The rows of a large table that keep(batch) selects, read in one streamed pass over cols."""
    path = os.path.join(ip.OUT_DIR, name + ".csv")
    skip = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            skip += 1
    types = {c: pa.string() for c in cols}
    types["value"] = pa.float64()
    reader = pcsv.open_csv(path, read_options=pcsv.ReadOptions(skip_rows=skip, block_size=1 << 24),
                           convert_options=pcsv.ConvertOptions(include_columns=cols, column_types=types))
    parts = [pa.Table.from_batches([b]).filter(keep(b)) for b in reader]
    return pa.concat_tables(parts).to_pandas()


def windows(e):
    """{year: (first day, last day)} of the event and its baseline years, local dates."""
    y0 = int(e["start"][:4])
    out = {}
    for y in [*e["baseline"], y0]:
        out[y] = (f"{y}{e['start'][4:]}", f"{y}{e['end'][4:]}")
    return out


def local_days(ts, tz):
    return pd.to_datetime(ts, utc=True).dt.tz_convert(tz).dt.strftime("%Y-%m-%d")


def build(e, log, retrieved):
    wins = windows(e)
    in_win = lambda d: any(a <= d <= b for a, b in wins.values())  # noqa: E731
    years = [str(y) for y in wins]
    rows, left = [], []
    base = dict(freq="P1D", geo="US-TX", node="", source="erw:event_window", source_url=METHOD_URL,
                retrieved_at=retrieved, vintage="", ba=e["ba"], event=e["event"])

    # prices: ERCOT's hub average, real-time 15-minute and day-ahead hourly
    p = stream(PRICES, lambda b: pc.and_(pc.equal(b.column("entity"), e["hub"]), pc.is_in(b.column("year"), pa.array(years))),
               ["entity", "variable", "ts_utc", "value", "market", "year"])
    p["day"] = local_days(p["ts_utc"], e["tz"])
    p = p[p["day"].map(in_win)]
    for market, var, n_need, pre in (("ercot_rtm", "spp_rtm", 96, "rt"), ("ercot_dam", "spp_dam", 24, "da")):
        g = p[(p["market"] == market) & (p["variable"] == var)].groupby("day")["value"]
        for day, v in g:
            if len(v) != n_need:
                left.append(f"{e['hub']} {market} {day}: {len(v)} of {n_need} intervals")
                continue
            for stat, val in (("mean", v.mean()), ("max", v.max())):
                rows.append(dict(base, entity=e["hub"], variable=f"{pre}_{stat}", ts_utc=f"{day}T00:00:00Z",
                                 value=r4(val), unit="USD/MWh", market=market))
    log(f"  prices: {len(p)} intervals read from {PRICES}")

    # demand and net generation: the workbook's own hourly columns (the emissions connector's extract)
    ex = em.latest_extract(e["ba"])
    if ex is None:
        raise RuntimeError(f"no extract of {e['ba']} under warehouse/raw/eia930_emissions/; nothing written")
    url, lm, got = em.extract_meta(ex)
    x = em.read_extract(ex)[["ts_utc", "demand_mwh", "net_generation_mwh"]]
    x["day"] = local_days(x["ts_utc"], e["tz"])
    x = x[x["day"].map(in_win)]
    # CO2 generated: the warehouse table
    c = stream(EMIS, lambda b: pc.and_(pc.equal(b.column("ba"), e["ba"]),
                                       pc.equal(b.column("variable"), "co2_emissions_generated")),
               ["entity", "variable", "ts_utc", "value", "ba"])
    x = x.merge(c[["ts_utc", "value"]].rename(columns={"value": "co2"}), on="ts_utc", how="left")
    for day, h in x.groupby("day"):
        t = f"{day}T00:00:00Z"
        eia = dict(base, entity=e["entity"], ts_utc=t, market="")
        if len(h) != 24 or h["demand_mwh"].isna().any():
            left.append(f"{e['entity']} demand {day}: {h['demand_mwh'].notna().sum()} of 24 hours")
        else:
            rows += [dict(eia, variable="demand_mwh", value=r4(h["demand_mwh"].sum()), unit="MWh"),
                     dict(eia, variable="demand_min_mw", value=r4(h["demand_mwh"].min()), unit="MW"),
                     dict(eia, variable="demand_max_mw", value=r4(h["demand_mwh"].max()), unit="MW")]
        if len(h) != 24 or h["net_generation_mwh"].isna().any():
            left.append(f"{e['entity']} net generation {day}: {h['net_generation_mwh'].notna().sum()} of 24 hours")
            continue
        rows.append(dict(eia, variable="net_generation_mwh", value=r4(h["net_generation_mwh"].sum()), unit="MWh"))
        if h["co2"].notna().sum() == 24 and h["net_generation_mwh"].sum() > 0:
            rows.append(dict(eia, variable="intensity_generation", unit="kgCO2/MWh",
                             value=r4(h["co2"].sum() * 1000 / h["net_generation_mwh"].sum())))
        else:
            left.append(f"{e['entity']} CO2 {day}: {h['co2'].notna().sum()} of 24 hours")
    log(f"  demand and net generation: {len(x)} hours from {os.path.relpath(ex, ROOT)} ({url}, Last-Modified {lm}); "
        f"CO2: {len(c)} rows of {EMIS}")

    # the event days against the mean of the baseline years' same calendar day
    df = pd.DataFrame(rows)
    y0 = int(e["start"][:4])
    for var in ("demand_mwh", "net_generation_mwh"):
        s = df[df["variable"] == var].set_index("ts_utc")["value"]
        for t, v in s.items():
            if int(t[:4]) != y0:
                continue
            b = [s.get(f"{y}{t[4:]}") for y in e["baseline"]]
            if any(x_ is None for x_ in b):
                left.append(f"{var} vs baseline {t[:10]}: a baseline day is missing")
                continue
            rows.append(dict(base, entity=e["entity"], ts_utc=t, market="", variable=f"{var}_vs_baseline",
                             value=r4(v - sum(b) / len(b)), unit="MWh"))
            # the event day minus the event year's previous day, when both are in the window
            prev = (pd.Timestamp(t[:10]) - pd.Timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z")
            if prev in s.index:
                rows.append(dict(base, entity=e["entity"], ts_utc=t, market="", variable=f"{var}_day_change",
                                 value=r4(v - s[prev]), unit="MWh"))
    return rows, left, (url, lm, got, ex)


def main():
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"event_window_{run_id}.log"))
    status = dict(table=NAME, market="derived", status="ok", detail="")
    try:
        retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        rows, left, used = [], [], []
        for e in EVENTS:
            r, lft, (url, lm, got, ex) = build(e, log, retrieved)
            rows += r
            left += lft
            used.append(f"{e['event']}: {os.path.relpath(ex, ROOT)} (EIA workbook {url}, Last-Modified {lm}, "
                        f"downloaded {got})")
            log(f"  {e['event']}: {len(r)} rows; left out: {len(lft)}")
        for x in left:
            log(f"  LEFT OUT {x}")
        out = pd.DataFrame(rows)[COLS].sort_values(["event", "entity", "variable", "ts_utc"]).reset_index(drop=True)
        if out.duplicated(["entity", "variable", "ts_utc", "event"]).any():  # session 36C: the key includes event
            raise RuntimeError("two rows share an (entity, variable, ts_utc, event) key")
        e = EVENTS[0]
        header = [
            "Energy Research Warehouse (ERW): event windows, daily figures around an event and the same calendar days "
            "of earlier years (Historical Event Analyzer v0, derived, session 36B)",
            "Shape: series (docs/datastandard.md v0), partition columns ba and event (decision 31); freq P1D, ts_utc the "
            "local operating day at 00:00:00Z (America/Chicago for ERCOT). A day is written only when every interval "
            "is present.",
            f"Retrieved: {run_id} (UTC) by warehouse/derived/event_window.py",
            f"Run log: warehouse/output/logs/event_window_{run_id}.log",
            f"Source: erw:event_window ERW derived table, events method (docs/methods/events.md), {METHOD_URL}",
            f"Derived from: {PRICES}; {EMIS}",
            "Also read: EIA's hourly demand and net generation from the per-BA workbooks (source "
            "eia:gridmonitor/knownissues/xls), the emissions connector's extract: " + "; ".join(used),
            f"Events: uri_2021 (Winter Storm Uri, ERCOT), window {e['start']} to {e['end']}, baseline the same calendar "
            f"days of {', '.join(map(str, e['baseline']))}.",
            "Demand during load shed is load served, not the demand customers would have had.",
            f"Days or variables left out, incomplete: {len(left)}" + (" (" + "; ".join(left[:10]) + ")" if left else ""),
        ]
        path = os.path.join(ip.OUT_DIR, NAME + ".csv")
        with open(path + ".tmp", "w", encoding="utf-8", newline="") as f:
            for h in header + [f"File holds {len(out)} rows, rewritten whole by this run."]:
                f.write("# " + h + "\n")
            out.to_csv(f, index=False, lineterminator="\n")
        os.replace(path + ".tmp", path)
        ip.update_sources([{"source": "erw:event_window", "publisher": "Energy Research Warehouse (ERW), derived",
                            "report": "Event windows, daily figures around an event and its baseline (docs/methods/events.md)",
                            "report_url": METHOD_URL, "document_list": "", "license": "public", "tables": [NAME]}])
        status["detail"] = f"{len(out)} rows; {len(left)} left out"
        print(f"{NAME}.csv: rows={len(out)}; left out {len(left)}")
        log(status["detail"])
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"event_window FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        status.update(status="failed", detail=tb.strip().splitlines()[-1][:300])
    ip.write_status("event_window", run_id, [status])
    log.close()
    return 0 if status["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
