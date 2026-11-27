"""ERW forecast (predict): the weather forecast as it was issued, and the airport's observed weather (chain 730, part F,
Samuel's order of 27 November 2026: "the demand model with the dated weather forecast window A now keeps, wherever
enough days are held"). Method note: docs/methods/predict.md, section 19.

Reads only. The National Weather Service's hourly forecast at one airport per ISO (warehouse/connectors/weather_nws.py):
  - weather_forecast_issued_hourly: every issue kept, from 26 November 2026 (data request 4 of chain 730);
  - weather_forecast_hourly: the latest forecast only; an hour's row is the last issue read before the table moved on,
    and its vintage (NWS's updateTime) says when that issue was made. A past hour whose kept row was issued before the
    hour the demand forecast is made was known then, and is used; a row issued later is not.
The airport's observed temperature, for the fit: noaa_station_weather_hourly (NOAA ISD-Lite and LCD v2, 2019 on), and
after its last hour weather_obs_hourly (NWS observations at the same airport).

Nothing known early: a forecast hour enters the forecast of target local day D only when its issue's vintage is no later
than the hour that day's demand forecast is made (20:00 UTC on D-1). Of the issues held by then, the latest is used.
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import predict_data as data  # noqa: E402

# the NWS airport of each ISO (weather_nws.py's choice), its NOAA name, and the places it stands for
AIRPORTS = {"KDFW": ("DFW", ["region-tex", "ba-erco"]), "KLAX": ("LAX", ["region-cal", "ba-ciso"]),
            "KLGA": ("LGA", ["region-ny", "ba-nyis"]), "KBOS": ("BOS", ["region-ne", "ba-isne"]),
            "KPHL": ("PHL", ["region-mida", "ba-pjm"]), "KIND": ("IND", ["region-midw", "ba-miso"]),
            "KOKC": ("OKC", ["region-cent", "ba-swpp"])}
PLACE_AIRPORT = {p: a for a, (_, ps) in AIRPORTS.items() for p in ps}
ISSUED = "weather_forecast_issued_hourly"
LATEST = "weather_forecast_hourly"
NOAA = "noaa_station_weather_hourly"
NWS_OBS = "weather_obs_hourly"


def issued_rows():
    """Every forecast row held, from both tables: airport, ts (the hour forecast, UTC), vintage (the issue), value
    (degrees F). A row of the latest-only table and the issued table with the same airport, hour and vintage is one
    forecast: kept once."""
    def build():
        a = data.read(ISSUED, ["entity", "variable", "ts_utc", "value", "vintage"],
                      lambda d: d["variable"].astype(str).str.startswith("temperature_f_lead"))
        b = data.read(LATEST, ["entity", "variable", "ts_utc", "value", "vintage"], lambda d: d["variable"] == "temperature_f")
        d = pd.concat([a, b], ignore_index=True)
        d["airport"] = d["entity"].str.split(":", n=1).str[1]
        d["vintage"] = pd.to_datetime(d["vintage"], utc=True, errors="coerce")
        d = d.dropna(subset=["vintage", "value"])
        d = d.drop_duplicates(subset=["airport", "ts", "vintage"], keep="first")
        return d[["airport", "ts", "vintage", "value"]].reset_index(drop=True)
    return data.cached("wxfc", [ISSUED, LATEST], build)


def observed():
    """Wide frame, index the UTC hour, one column an NWS airport of AIRPORTS: the observed temperature, degrees F;
    NOAA's measured hours, and NWS's observations for the hours after NOAA's last."""
    def build():
        names = {v[0]: k for k, v in AIRPORTS.items()}
        n = data.read(NOAA, ["variable", "ts_utc", "value", "node"],
                      lambda d: (d["variable"] == "temperature_f") & d["node"].isin(list(names)))
        w = data.read(NWS_OBS, ["entity", "variable", "ts_utc", "value"], lambda d: d["variable"] == "temperature_f")
        cols = {}
        for code, k in names.items():
            g = n[n["node"] == code]
            s = pd.Series(g["value"].to_numpy(dtype=float), index=pd.DatetimeIndex(g["ts"])).sort_index()
            s = s[~s.index.duplicated(keep="last")]
            h = w[w["entity"] == "nws:" + k]
            t = pd.Series(h["value"].to_numpy(dtype=float), index=pd.DatetimeIndex(h["ts"])).sort_index()
            t = t[~t.index.duplicated(keep="last")]
            last = s.index.max() if len(s) else None
            if last is not None:
                t = t[t.index > last]
            cols[k] = pd.concat([s, t]).sort_index()
        df = pd.DataFrame(cols)
        df = df.reindex(pd.date_range(df.index.min(), df.index.max(), freq="h"))
        df.index.name = "ts"
        return df
    return data.cached("wxobs", [NOAA, NWS_OBS], build)


def forecast_matrix(rows, airport, tz, days, made_hour=20):
    """F[i, k]: the temperature forecast for local day days[i], local hour k, from the latest issue whose vintage is no
    later than made_hour UTC on the day before; V[i]: that day's latest vintage used (NaT where none). The autumn's
    repeated hour takes the mean of its two; a lone missing hour inside a day is the mean of its neighbours (as the
    regressors of the regression); a day with any other hour missing has no row."""
    r = rows[rows["airport"] == airport]
    F = np.full((len(days), 24), np.nan)
    V = np.full(len(days), np.datetime64("NaT"), dtype="datetime64[ns]")
    if not len(r):
        return F, V
    loc = r["ts"].dt.tz_convert(tz)
    r = r.assign(day=loc.dt.tz_localize(None).dt.normalize(), hour=loc.dt.hour)
    r = r.assign(made=(r["day"] - pd.Timedelta(days=1)).dt.tz_localize("UTC") + pd.Timedelta(hours=made_hour))
    r = r[r["vintage"] <= r["made"]]
    if not len(r):
        return F, V
    r = r.sort_values("vintage").drop_duplicates(subset=["ts"], keep="last")
    pos = {d: i for i, d in enumerate(pd.DatetimeIndex(days))}
    g = r.groupby(["day", "hour"]).agg(value=("value", "mean"), vintage=("vintage", "max")).reset_index()
    for d, h, v, vt in zip(g["day"], g["hour"], g["value"], g["vintage"]):
        i = pos.get(d)
        if i is not None:
            F[i, h] = v
            if np.isnat(V[i]) or vt.to_datetime64() > V[i]:
                V[i] = vt.tz_convert(None).to_datetime64()
    lone = np.isnan(F[:, 1:23]) & np.isfinite(F[:, 0:22]) & np.isfinite(F[:, 2:24])
    F[:, 1:23] = np.where(lone, (F[:, 0:22] + F[:, 2:24]) / 2.0, F[:, 1:23])
    F[~np.isfinite(F).all(axis=1)] = np.nan
    return F, V
