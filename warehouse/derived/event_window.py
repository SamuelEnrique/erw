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

Session 36C adds covid_2020 (build_covid): the seven ISO balancing authorities and US48, 2020-03-01 to 2020-05-31, each
BA's local day, against the same weekday 364 and 728 days earlier where the extracts reach (they start 2018-07-01, so
2019 alone). Variables demand_mwh, demand_min_mw, demand_max_mw, intensity_generation, demand_mwh_vs_baseline,
demand_pct_vs_baseline (pct), the same two per whole week (freq P1W, at the week's first day, a Sunday) and ERCOT's hub
rt_mean and da_mean. A local day has 23 hours on the spring change to daylight time, and that day is complete.

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
# Session 36C: COVID-19, spring 2020, all seven ISO balancing authorities and US48. The baseline is weekday-aligned: the
# same weekday 364 and 728 days earlier. Each BA's local day: ERCOT operating days (America/Chicago) for ERCO, the time
# zones of storage_daily_cycle for the others (MISO on Eastern Standard Time all year, as its market day), Pacific for
# CISO and Eastern for NYIS and PJM.
COVID = dict(event="covid_2020", start="2020-03-01", end="2020-05-31", offsets=[364, 728], hub="ercot:HB_HUBAVG",
             hub_ba="erco",
             bas={"ciso": ("CISO", "America/Los_Angeles", "US-CA"),
                  "erco": ("ERCO", "America/Chicago", "US-TX"),
                  "isne": ("ISNE", "America/New_York", "US-CT,US-MA,US-ME,US-NH,US-RI,US-VT"),
                  "miso": ("MISO", "EST", "US-AR,US-IL,US-IN,US-IA,US-KY,US-LA,US-MI,US-MN,US-MS,US-MO,US-MT,"
                                         "US-ND,US-SD,US-TX,US-WI"),
                  "nyis": ("NYIS", "America/New_York", "US-NY"),
                  "pjm": ("PJM", "America/New_York", "US-DE,US-DC,US-IL,US-IN,US-KY,US-MD,US-MI,US-NJ,US-NC,US-OH,"
                                                     "US-PA,US-TN,US-VA,US-WV"),
                  "swpp": ("SWPP", "America/Chicago", "US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,"
                                                      "US-OK,US-SD,US-TX,US-WY"),
                  "us48": ("US48", "America/New_York", "US")}, weekly=True, prices="mean", label="COVID-19")
# Session 39: three more events on the template, the same weekday-aligned baseline (364 and 728 days, both held).
# max_vs: the day's peak hour against the baseline days' too; prices "full": the hub's daily max beside its mean.
CAISO_HEAT = dict(event="caiso_heat_2020", label="the August 2020 heat wave, CAISO", start="2020-08-10", end="2020-08-24",
                  offsets=[364, 728], hub=None, bas={"ciso": COVID["bas"]["ciso"]}, max_vs=True)
ELLIOTT = dict(event="elliott_2022", label="Winter Storm Elliott, six grids", start="2022-12-19", end="2022-12-29",
               offsets=[364, 728], hub="ercot:HB_HUBAVG", hub_ba="erco", prices="full", max_vs=True,
               bas={k: COVID["bas"][k] for k in ("erco", "isne", "miso", "nyis", "pjm", "swpp")})
ERCOT_HEAT = dict(event="ercot_heat_2023", label="the summer 2023 heat, ERCOT", start="2023-08-01", end="2023-09-10",
                  offsets=[364, 728], hub="ercot:HB_HUBAVG", hub_ba="erco", prices="full", max_vs=True,
                  bas={"erco": COVID["bas"]["erco"]})
# Session 58: CAISO's September 2022 heat (Flex Alerts on ten days, EEA3 on 2022-09-06; caiso_grid_emergencies), on the
# CAISO 2020 template: CISO, the same weekday 364 and 728 days earlier
CAISO_HEAT_2022 = dict(event="caiso_heat_2022", label="the September 2022 heat wave, CAISO", start="2022-08-31", end="2022-09-09",
                       offsets=[364, 728], hub=None, bas={"ciso": COVID["bas"]["ciso"]}, max_vs=True)
# Session 64: two events of the year the second hub-price pull added (2024-09-01 to 2025-08-31), chosen from the data: the
# days of that year's highest winter and summer peak hours of demand served in PJM, MISO, NYISO and ISO-NE (EIA-930).
# hubs: the other ISOs' main hubs from iso_hub_prices_history, each on its grid's local day (no baseline price: the
# history starts 2024-09-01, so the same weekdays 364 and 728 days earlier are not held).
COLD_2025 = dict(event="cold_2025", label="the January 2025 cold, six grids", start="2025-01-17", end="2025-01-26",
                 offsets=[364, 728], hub="ercot:HB_HUBAVG", hub_ba="erco", prices="full", max_vs=True,
                 bas={k: COVID["bas"][k] for k in ("erco", "isne", "miso", "nyis", "pjm", "swpp")},
                 hubs=["miso:INDIANA.HUB", "nyiso:N.Y.C.", "isone:.H.INTERNAL_HUB", "spp:SPPNORTH_HUB"])
EAST_HEAT_2025 = dict(event="east_heat_2025", label="the June 2025 heat, four eastern grids", start="2025-06-20", end="2025-06-28",
                      offsets=[364, 728], hub=None, max_vs=True,
                      bas={k: COVID["bas"][k] for k in ("pjm", "nyis", "isne", "miso")},
                      hubs=["nyiso:N.Y.C.", "isone:.H.INTERNAL_HUB", "miso:INDIANA.HUB"])
MULTI = [COVID, CAISO_HEAT, ELLIOTT, ERCOT_HEAT, CAISO_HEAT_2022, COLD_2025, EAST_HEAT_2025]
HUB_HISTORY = "iso_hub_prices_history"
HUB_BA = {"miso": "miso", "nyiso": "nyis", "isone": "isne", "spp": "swpp", "caiso": "ciso"}  # each hub's grid (its local day)
_hub_cache = {}


def hub_rows(e, days, held_by_ba, base, left, log):
    """Session 64: the daily mean and highest real-time and day-ahead price of each hub in e["hubs"], from
    iso_hub_prices_history, on its grid's local day, for the window and whatever baseline days the history holds. A day
    is written only when every interval is there (real-time 15-minute means, MISO's hourly real-time; hourly day-ahead)."""
    if not e.get("hubs"):
        return []
    if HUB_HISTORY not in _hub_cache:
        path = os.path.join(ip.OUT_DIR, HUB_HISTORY + ".csv")
        if not os.path.exists(path):
            left.append(f"{HUB_HISTORY} is not on this machine: no hub prices for {e['event']}")
            return []
        _hub_cache[HUB_HISTORY] = ip.read_series(path)
    h = _hub_cache[HUB_HISTORY]
    shift = lambda d, o: (pd.Timestamp(d) - pd.Timedelta(days=o)).strftime("%Y-%m-%d")  # noqa: E731
    rows = []
    for hub in e["hubs"]:
        iso = hub.split(":")[0]
        ba = HUB_BA[iso]
        tz = e["bas"][ba][1]
        want = set(days) | {shift(d, o) for d in days for o in held_by_ba.get(ba, [])}
        p = h[h["entity"] == hub].copy()
        p["day"] = local_days(p["ts_utc"], tz)
        p = p[p["day"].isin(want)]
        n_read = 0
        for market, pre in ((f"{iso}_rtm", "rt"), (f"{iso}_dam", "da")):
            m = p[p["market"] == market]
            n_read += len(m)
            per_hour = 4 if (len(m) and m["freq"].iloc[0] == "PT15M") else 1
            g = m.groupby("day")
            for d in sorted(want):
                if d not in g.groups:
                    if d in days:
                        left.append(f"{hub} {market} {d}: not held")
                    continue
                v = g.get_group(d)["value"]
                need = per_hour * hours_in(d, tz)
                if len(v) != need:
                    left.append(f"{hub} {market} {d}: {len(v)} of {need} intervals")
                    continue
                geo = g.get_group(d)["geo"].iloc[0]
                for stat, val in (("mean", v.mean()), ("max", v.max())):
                    rows.append(dict(base, entity=hub, variable=f"{pre}_{stat}", ts_utc=f"{d}T00:00:00Z", geo=geo,
                                     value=r4(val), unit="USD/MWh", market=market, ba=ba))
        log(f"  {e['event']} {hub}: {n_read} intervals read from {HUB_HISTORY}")
    return rows


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


HIST = "eia930_all_history"


def history_hours(resp, before):
    """Session 49: a BA's hours from eia930_all_history (EIA-930 six-month files) before an instant, as the extract's
    columns (ts_utc, demand_mwh, net_generation_mwh; EIA's MW over an hour is its MWh). Empty if the table is absent."""
    path = os.path.join(ip.OUT_DIR, HIST + ".csv")
    if not os.path.exists(path):
        return pd.DataFrame(columns=["ts_utc", "demand_mwh", "net_generation_mwh"])
    h = ip.read_series(path, cols=ip.SERIES_COLS + ["ba"])
    h = h[h["entity"] == f"eia930:{resp}"]
    if not len(h):  # US48 is not a balancing authority in the six-month files
        return pd.DataFrame(columns=["ts_utc", "demand_mwh", "net_generation_mwh"])
    w = h.pivot_table(index="ts_utc", columns="variable", values="value").reset_index()
    w = w.rename(columns={"demand_mw": "demand_mwh", "net_generation_mw": "net_generation_mwh"})
    w["ts_utc"] = pd.to_datetime(w["ts_utc"], utc=True)
    b = pd.to_datetime(pd.Series([before]), utc=True).iloc[0]
    return w[w["ts_utc"] < b][["ts_utc", "demand_mwh", "net_generation_mwh"]]


# Session 49: the weather at each grid's stations (noaa_isd_hourly), per station and local day of every event and baseline
WEATHER = "noaa_isd_hourly"


def build_weather(log, retrieved):
    """Per station and local day (the station's grid's time zone), for every day an event's rows cover: the mean of the
    hourly temperatures (each clock hour's observations averaged first), the minimum and maximum of every observation,
    and heating and cooling degree days at 65 F from (max + min) / 2, the National Weather Service's daily mean. A day
    with observations in fewer than 20 clock hours is not written."""
    import noaa_isd
    path = os.path.join(ip.OUT_DIR, WEATHER + ".csv")
    if not os.path.exists(path):
        return [], [f"{WEATHER} is not on this machine: no weather rows"], []
    w = ip.read_series(path, cols=ip.SERIES_COLS + ["ba", "x_station_id"])
    w = w[w["variable"] == "temperature_f"]
    w["ts"] = pd.to_datetime(w["ts_utc"], utc=True)
    rows, left = [], []
    plans = [(e["event"], e["start"], e["end"], [f"{y}" for y in e["baseline"]], [e["ba"]]) for e in EVENTS] + \
        [(m["event"], m["start"], m["end"], m["offsets"], list(m["bas"])) for m in MULTI]
    for ev, start, end, base, bas in plans:
        days = [d.strftime("%Y-%m-%d") for d in pd.date_range(start, end, freq="D")]
        want = set(days)
        for b in base:
            if isinstance(b, int):
                want |= {(pd.Timestamp(d) - pd.Timedelta(days=b)).strftime("%Y-%m-%d") for d in days}
            else:
                want |= {f"{b}{d[4:]}" for d in days}
        for code, (sid, ba, tz, _) in noaa_isd.STATIONS.items():
            if ba not in bas:
                continue
            g = w[w["entity"] == f"noaa:{code}"].copy()
            if not len(g):
                left.append(f"noaa:{code} {ev}: no observations held")
                continue
            local = g["ts"].dt.tz_convert(tz)
            g["day"], g["hour"] = local.dt.strftime("%Y-%m-%d"), local.dt.hour
            g = g[g["day"].isin(want)]
            for day, h in g.groupby("day"):
                if h["hour"].nunique() < 20:
                    left.append(f"noaa:{code} {day}: observations in {h['hour'].nunique()} clock hours")
                    continue
                hi, lo = h["value"].max(), h["value"].min()
                mid = (hi + lo) / 2
                base_row = dict(entity=f"noaa:{code}", ts_utc=f"{day}T00:00:00Z", freq="P1D", geo="", market="", node=sid,
                                source="erw:event_window", source_url=METHOD_URL, retrieved_at=retrieved, vintage="", ba=ba, event=ev)
                rows += [dict(base_row, variable="temp_mean_f", value=r4(h.groupby("hour")["value"].mean().mean()), unit="degF"),
                         dict(base_row, variable="temp_min_f", value=r4(lo), unit="degF"),
                         dict(base_row, variable="temp_max_f", value=r4(hi), unit="degF"),
                         dict(base_row, variable="hdd_65f", value=r4(max(0.0, 65 - mid)), unit="degF-day"),
                         dict(base_row, variable="cdd_65f", value=r4(max(0.0, mid - 65)), unit="degF-day")]
    log(f"  weather: {len(rows)} station-day rows from {WEATHER}")
    return rows, left, [f"weather: {WEATHER} (NOAA NCEI ISD hourly temperature)"]


def hours_in(day, tz):
    """The hours of a local day: 23 on the spring change to daylight time, 25 on the autumn change, else 24."""
    a = pd.Timestamp(day).tz_localize(tz)
    return int(((a + pd.DateOffset(days=1)).normalize() - a).total_seconds() // 3600)


def build_covid(e, log, retrieved):
    """covid_2020 (session 36C): per BA and local day, demand served and carbon intensity in the window and on the
    weekday-aligned baseline days, the event days against the baseline (MWh and percent), the same for each whole week
    of the window, and ERCOT's hub prices for context. A baseline offset is used only where the extracts reach it."""
    days = [d.strftime("%Y-%m-%d") for d in pd.date_range(e["start"], e["end"], freq="D")]
    shift = lambda d, o: (pd.Timestamp(d) - pd.Timedelta(days=o)).strftime("%Y-%m-%d")  # noqa: E731
    rows, left, used = [], [], []
    base = dict(freq="P1D", node="", source="erw:event_window", source_url=METHOD_URL, retrieved_at=retrieved,
                vintage="", event=e["event"])

    # CO2 generated, one streamed pass over eia930_all_emissions for every BA, the years the days can fall in
    years = sorted({shift(d, o)[:4] for d in days for o in [0] + e["offsets"]})
    c = stream(EMIS, lambda b: pc.and_(pc.and_(pc.is_in(b.column("ba"), pa.array(list(e["bas"]))),
                                               pc.equal(b.column("variable"), "co2_emissions_generated")),
                                       pc.is_in(pc.utf8_slice_codeunits(b.column("ts_utc"), 0, 4), pa.array(years))),
               ["entity", "variable", "ts_utc", "value", "ba"])
    log(f"  {e['event']} CO2: {len(c)} rows of {EMIS} (years {', '.join(years)})")

    held_by_ba = {}
    for ba, (resp, tz, geo) in e["bas"].items():
        entity = f"eia930:{resp}"
        ex = em.latest_extract(ba)
        if ex is None:
            raise RuntimeError(f"no extract of {ba} under warehouse/raw/eia930_emissions/; nothing written")
        url, lm, got = em.extract_meta(ex)
        used.append(f"{ba}: {os.path.relpath(ex, ROOT)} (EIA workbook {url}, Last-Modified {lm}, downloaded {got})")
        x = em.read_extract(ex)[["ts_utc", "demand_mwh", "net_generation_mwh"]]
        # session 49: the hours before the extract begins (2018-06-30), from EIA's six-month files (eia930_all_history)
        hist = history_hours(resp, x["ts_utc"].min())
        if len(hist):
            x = pd.concat([hist, x], ignore_index=True)
            used.append(f"{ba}: {len(hist)} hours before the extract from {HIST}")
        x["day"] = local_days(x["ts_utc"], tz)
        first = x.loc[x["demand_mwh"].notna(), "day"].min()
        # an offset whose baseline days start before the extract's first hour of demand is not held: left out whole
        held = [o for o in e["offsets"] if shift(days[0], o) > first]
        for o in e["offsets"]:
            if o not in held:
                left.append(f"{entity} baseline {o} days earlier ({shift(days[0], o)} to {shift(days[-1], o)}): not "
                            f"held, the extract's demand starts {first}")
        held_by_ba[ba] = held
        want = set(days) | {shift(d, o) for d in days for o in held}
        x = x[x["day"].isin(want)]
        x = x.merge(c.loc[c["ba"] == ba, ["ts_utc", "value"]].rename(columns={"value": "co2"}), on="ts_utc", how="left")
        eia0 = dict(base, entity=entity, geo=geo, market="", ba=ba)
        dem, mx = {}, {}
        for day, h in x.groupby("day"):
            eia = dict(eia0, ts_utc=f"{day}T00:00:00Z")
            n = hours_in(day, tz)  # a complete day has every hour of the local day, 23 on 2019-03-10 and 2020-03-08
            if len(h) != n or h["demand_mwh"].isna().any():
                left.append(f"{entity} demand {day}: {h['demand_mwh'].notna().sum()} of {n} hours")
            else:
                dem[day] = h["demand_mwh"].sum()
                mx[day] = h["demand_mwh"].max()
                rows += [dict(eia, variable="demand_mwh", value=r4(dem[day]), unit="MWh"),
                         dict(eia, variable="demand_min_mw", value=r4(h["demand_mwh"].min()), unit="MW"),
                         dict(eia, variable="demand_max_mw", value=r4(h["demand_mwh"].max()), unit="MW")]
            if len(h) == n and h["net_generation_mwh"].notna().all() and h["co2"].notna().sum() == n \
                    and h["net_generation_mwh"].sum() > 0:
                rows.append(dict(eia, variable="intensity_generation", unit="kgCO2/MWh",
                                 value=r4(h["co2"].sum() * 1000 / h["net_generation_mwh"].sum())))
            else:
                left.append(f"{entity} intensity {day}: net generation {h['net_generation_mwh'].notna().sum()}, "
                            f"CO2 {h['co2'].notna().sum()} of {n} hours")
        # each event day against the mean of its held baseline days (same weekday, 364 or 728 days earlier)
        for d in days:
            b = [dem.get(shift(d, o)) for o in held]
            if d not in dem or not held or any(v is None for v in b):
                left.append(f"{entity} demand vs baseline {d}: the day or a baseline day is missing")
                continue
            bm = sum(b) / len(b)
            eia = dict(eia0, ts_utc=f"{d}T00:00:00Z")
            rows += [dict(eia, variable="demand_mwh_vs_baseline", value=r4(dem[d] - bm), unit="MWh"),
                     dict(eia, variable="demand_pct_vs_baseline", value=r4((dem[d] / bm - 1) * 100), unit="pct")]
            if e.get("max_vs"):  # session 39: the day's peak hour against the baseline days' peak hours
                bx = sum(mx[shift(d, o)] for o in held) / len(held)
                rows += [dict(eia, variable="demand_max_mw_vs_baseline", value=r4(mx[d] - bx), unit="MW"),
                         dict(eia, variable="demand_max_pct_vs_baseline", value=r4((mx[d] / bx - 1) * 100), unit="pct")]
        # whole weeks of the window from its first day (2020-03-01, a Sunday): the week's demand against the mean of
        # its baseline weeks' demand
        for i in range(0, len(days) - 6 if e.get("weekly") else 0, 7):  # session 39: weeks for covid_2020 only
            wk = days[i:i + 7]
            cur = [dem.get(d) for d in wk]
            bw = [[dem.get(shift(d, o)) for d in wk] for o in held]
            if not held or any(v is None for v in cur) or any(v is None for w in bw for v in w):
                left.append(f"{entity} week of {wk[0]}: a day or a baseline day is missing")
                continue
            bm = sum(sum(w) for w in bw) / len(bw)
            eia = dict(eia0, ts_utc=f"{wk[0]}T00:00:00Z", freq="P1W")
            rows += [dict(eia, variable="demand_mwh_vs_baseline_week", value=r4(sum(cur) - bm), unit="MWh"),
                     dict(eia, variable="demand_pct_vs_baseline_week", value=r4((sum(cur) / bm - 1) * 100),
                          unit="pct")]
        log(f"  {e['event']} {ba}: {len(x)} hours from {os.path.relpath(ex, ROOT)} ({url}, Last-Modified {lm}); "
            f"baseline offsets held {held}")

    rows += hub_rows(e, days, held_by_ba, base, left, log)  # session 64: the other ISOs' hubs
    # ERCOT's hub prices for context: the window and ERCO's held baseline days (session 39: none for an event without a
    # hub; daily max too where prices is "full")
    if not e.get("hub"):
        return rows, left, used
    want = set(days) | {shift(d, o) for d in days for o in held_by_ba[e["hub_ba"]]}
    p = stream(PRICES, lambda b: pc.and_(pc.equal(b.column("entity"), e["hub"]),
                                         pc.is_in(b.column("year"), pa.array(sorted({d[:4] for d in want})))),
               ["entity", "variable", "ts_utc", "value", "market", "year"])
    p["day"] = local_days(p["ts_utc"], e["bas"][e["hub_ba"]][1])
    p = p[p["day"].isin(want)]
    for market, var, per_hour, pre in (("ercot_rtm", "spp_rtm", 4, "rt"), ("ercot_dam", "spp_dam", 1, "da")):
        g = p[(p["market"] == market) & (p["variable"] == var)].groupby("day")["value"]
        for day, v in g:
            n_need = per_hour * hours_in(day, e["bas"][e["hub_ba"]][1])  # 92 and 23 on the spring change
            if len(v) != n_need:
                left.append(f"{e['hub']} {market} {day}: {len(v)} of {n_need} intervals")
                continue
            rows.append(dict(base, entity=e["hub"], variable=f"{pre}_mean", ts_utc=f"{day}T00:00:00Z", geo="US-TX",
                             value=r4(v.mean()), unit="USD/MWh", market=market, ba=e["hub_ba"]))
            if e.get("prices") == "full":
                rows.append(dict(base, entity=e["hub"], variable=f"{pre}_max", ts_utc=f"{day}T00:00:00Z", geo="US-TX",
                                 value=r4(v.max()), unit="USD/MWh", market=market, ba=e["hub_ba"]))
    log(f"  {e['event']} prices: {len(p)} intervals read from {PRICES}")
    return rows, left, used


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
        for m in MULTI:  # session 36C covid_2020; session 39 the three events after it
            r, lft, cu = build_covid(m, log, retrieved)
            rows += r
            left += lft
            used.append(f"{m['event']}: " + "; ".join(cu))
            log(f"  {m['event']}: {len(r)} rows; left out: {len(lft)}")
        r, lft, cu = build_weather(log, retrieved)  # session 49
        rows += r
        left += lft
        used += cu
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
            "local operating day at 00:00:00Z (America/Chicago for ERCOT, each BA's own zone for the others; weekly rows "
            "freq P1W at the week's first day). A day is written only when every interval is present. Key (entity, "
            "variable, ts_utc, event), decision 32.",
            f"Retrieved: {run_id} (UTC) by warehouse/derived/event_window.py",
            f"Run log: warehouse/output/logs/event_window_{run_id}.log",
            f"Source: erw:event_window ERW derived table, events method (docs/methods/events.md), {METHOD_URL}",
            f"Derived from: {PRICES}; {EMIS}; {HIST}; {WEATHER}; {HUB_HISTORY} (session 64)",
            "Also read: EIA's hourly demand and net generation from the per-BA workbooks (source "
            "eia:gridmonitor/knownissues/xls), the emissions connector's extract: " + "; ".join(used),
            f"Events: uri_2021 (Winter Storm Uri, ERCOT), window {e['start']} to {e['end']}, baseline the same calendar "
            f"days of {', '.join(map(str, e['baseline']))}. covid_2020 (COVID-19, seven ISO BAs and US48, session 36C), "
            f"window {COVID['start']} to {COVID['end']}, baseline the same weekday "
            f"{' and '.join(map(str, COVID['offsets']))} days earlier where held. Session 39: "
            + "; ".join(f"{m['event']} ({m['label']}), window {m['start']} to {m['end']}, the same weekday 364 and 728 "
                        f"days earlier" for m in MULTI[1:]) + ".",
            "Demand during load shed is load served, not the demand customers would have had.",
            "Session 49: COVID-19's 728-day baseline (2018-03-04 to 2018-06-03) from EIA's six-month files (eia930_all_history; "
            "no CO2 for those hours, so no intensity). Weather per station and local day (entity noaa:<station>, node the ISD "
            "station id): temp_mean_f (the mean of the clock hours' means), temp_min_f, temp_max_f, hdd_65f and cdd_65f "
            "(degree days at 65 F from (max + min) / 2); a day with fewer than 20 clock hours observed is not written.",
            "Session 64: cold_2025 and east_heat_2025 add the other ISOs' main hubs (entity <iso>:<hub>, from "
            f"{HUB_HISTORY}): rt_mean, rt_max, da_mean, da_max per the grid's local day, written only when every interval is "
            "there; the history starts 2024-09-01, so these hubs have no baseline days. No weather is held for these two events.",
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
