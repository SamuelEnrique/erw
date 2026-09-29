#!/usr/bin/env python3
"""The daily cycle of battery storage per balancing authority, from eia930_all_storage (session 31, Part B2).

Energy Research Warehouse (ERW). For each BA and each complete local day (every hour present: 24, or 23 and 25 on
the daylight saving days), from EIA-930's hourly battery net generation (positive discharging, negative charging):

    mwh_discharged       sum of the positive hourly values x 1 hour, MWh
    mwh_charged          sum of the negative hourly values x 1 hour, as a positive number, MWh
    peak_discharge_hour  the local hour (0 to 23, the hour's start) of the day's largest positive value, unit hour;
                         absent on a day with no discharge; the earliest such hour on a tie
    peak_charge_hour     the local hour of the day's most negative value, unit hour; absent on a day with no charge
    round_trip_ratio     mwh_discharged / mwh_charged, where both are above zero, unit ratio. It is the ratio of the
                         day's energy out to energy in as EIA-930 reports them, not a measured efficiency: charge
                         carried across midnight and batteries reported in other fuel types move it

Local time: ERCO and SWPP America/Chicago, MISO EST (fixed UTC-5, as MISO publishes), ISNE America/New_York, US48
America/New_York (the Eastern time EIA's Grid Monitor shows by default). Writes warehouse/output/storage_daily_cycle.csv,
rewritten whole each run. Method: docs/methods/storage.md.

Session 34: CAISO reports no battery series in EIA-930, so its rows come from CAISO's own data, caiso_battery_storage
(Today's Outlook, 5-minute, Total batteries). Each hour is the mean of its twelve 5-minute values (MW over the hour, so
MWh); a Pacific day is complete when every 5-minute interval is present; the same five variables follow from those
hourly values. CAISO's rows are marked by their source, erw:storage_daily_cycle_caiso (entity caiso:ISO, ba ciso).

    python warehouse/derived/storage_daily_cycle.py
"""

import datetime as dt
import os
import sys
import traceback

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

NAME = "storage_daily_cycle"
INPUT = "eia930_all_storage"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/storage.md"
CAISO_INPUT = "caiso_battery_storage"  # session 34
CAISO_SOURCE = "erw:storage_daily_cycle_caiso"
CAISO_METHOD_URL = METHOD_URL + "#caiso"
CAISO_TZ = "America/Los_Angeles"
TZ = {"erco": "America/Chicago", "swpp": "America/Chicago", "miso": "EST", "isne": "America/New_York",
      "us48": "America/New_York"}
COLS = ip.SERIES_COLS + ["ba"]


def r3(v):
    from decimal import Decimal, ROUND_HALF_UP
    return float(Decimal(repr(float(v))).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP))


def hours_in(day, tz):
    """Hours in a local day: 24, or 23 and 25 on the daylight saving days."""
    return int((pd.Timestamp(day + dt.timedelta(days=1)).tz_localize(tz)
                - pd.Timestamp(day).tz_localize(tz)) / pd.Timedelta(hours=1))


def day_rows(x, who, day, retrieved):
    """One complete local day's rows from its hourly values x (columns value, ts, hour)."""
    t = f"{day.isoformat()}T00:00:00Z"
    pos, neg = x["value"].clip(lower=0).sum(), (-x["value"].clip(upper=0)).sum()
    url = CAISO_METHOD_URL if who["source"] == CAISO_SOURCE else METHOD_URL
    base = dict(entity=who["entity"], ts_utc=t, freq="P1D", geo=who["geo"], market="", node="",
                source=who["source"], source_url=url, retrieved_at=retrieved, vintage="", ba=who["ba"])
    rows = [dict(base, variable="mwh_discharged", value=r3(pos), unit="MWh"),
            dict(base, variable="mwh_charged", value=r3(neg), unit="MWh")]
    if x["value"].max() > 0:
        rows.append(dict(base, variable="peak_discharge_hour", unit="hour",
                         value=int(x.sort_values(["value", "ts"], ascending=[False, True])["hour"].iloc[0])))
    if x["value"].min() < 0:
        rows.append(dict(base, variable="peak_charge_hour", unit="hour",
                         value=int(x.sort_values(["value", "ts"], ascending=[True, True])["hour"].iloc[0])))
    if pos > 0 and neg > 0:
        rows.append(dict(base, variable="round_trip_ratio", value=r3(pos / neg), unit="ratio"))
    return rows


def caiso_rows(retrieved, log):
    """Session 34: CAISO's daily cycle from its own 5-minute Total batteries series (caiso_battery_storage).
    Each hour is the mean of its twelve 5-minute values; a Pacific day is written only with every interval present.
    A missing input fails loudly: the table would otherwise lose CAISO's history."""
    path = os.path.join(ip.OUT_DIR, CAISO_INPUT + ".csv")
    with open(path, encoding="utf-8") as f:
        skip = sum(1 for line in f if line.startswith("#"))
    c = pd.read_csv(path, skiprows=skip, usecols=["entity", "variable", "ts_utc", "value", "geo"],
                    dtype={"value": float}, keep_default_na=False)
    c = c[c["variable"] == "batteries_mw"].drop_duplicates(["entity", "ts_utc"])
    c["ts"] = pd.to_datetime(c["ts_utc"], utc=True)
    c = c.assign(day=c["ts"].dt.tz_convert(CAISO_TZ).dt.date, hour_ts=c["ts"].dt.floor("h"))
    rows, n_days, n_left = [], 0, 0
    for day, x in c.groupby("day"):
        if len(x) != 12 * hours_in(day, CAISO_TZ):
            n_left += 1
            continue
        h = x.groupby("hour_ts", as_index=False)["value"].mean().rename(columns={"hour_ts": "ts"})
        h["hour"] = h["ts"].dt.tz_convert(CAISO_TZ).dt.hour
        n_days += 1
        rows += day_rows(h, dict(entity=x["entity"].iloc[0], geo=x["geo"].iloc[0], source=CAISO_SOURCE, ba="ciso"),
                         day, retrieved)
    log(f"  ciso ({CAISO_INPUT}): {n_days} complete Pacific days, {n_left} partial days left out ({CAISO_TZ})")
    return rows


def main():
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"storage_daily_cycle_{run_id}.log"))
    status = dict(table=NAME, market="derived", status="ok", detail="")
    try:
        d = ip.read_series(os.path.join(ip.OUT_DIR, INPUT + ".csv"), COLS)
        d["ts"] = pd.to_datetime(d["ts_utc"], utc=True)
        retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        rows = []
        for ba, g in d.groupby("ba"):
            tz = TZ[ba]
            local = g["ts"].dt.tz_convert(tz)
            g = g.assign(day=local.dt.date, hour=local.dt.hour)
            entity, geo = g["entity"].iloc[0], g["geo"].iloc[0]
            n_days = n_left = 0
            for day, x in g.groupby("day"):
                if len(x) != hours_in(day, tz):
                    n_left += 1
                    continue
                n_days += 1
                rows += day_rows(x, dict(entity=entity, geo=geo, source="erw:storage_daily_cycle", ba=ba), day,
                                 retrieved)
            log(f"  {ba}: {n_days} complete local days, {n_left} partial days left out ({tz})")
        caiso = caiso_rows(retrieved, log)  # session 34
        rows += caiso
        out = pd.DataFrame(rows)[COLS].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        header = [
            "Energy Research Warehouse (ERW): battery storage daily cycle per balancing authority, from EIA-930 "
            "(derived, session 31) and, for CAISO, from CAISO's own data (session 34)",
            "Shape: series (docs/datastandard.md v0), partition column ba; freq P1D, ts_utc the local day at "
            "00:00:00Z (ERCO, SWPP America/Chicago; MISO EST; ISNE, US48 America/New_York; CISO America/Los_Angeles). "
            "Complete local days only.",
            f"Retrieved: {run_id} (UTC) by warehouse/derived/storage_daily_cycle.py",
            f"Run log: warehouse/output/logs/storage_daily_cycle_{run_id}.log",
            f"Source: erw:storage_daily_cycle ERW derived table, storage method (docs/methods/storage.md), {METHOD_URL}",
            f"Source: {CAISO_SOURCE} the CAISO rows (ba ciso, entity caiso:ISO), from CAISO's Today's Outlook Total "
            f"batteries, 5-minute values averaged to hours, {CAISO_METHOD_URL}",
            f"Derived from: {INPUT}; {CAISO_INPUT}",
            "Variables: mwh_discharged, mwh_charged (sums of the positive and of the negative hourly net generation, "
            "MWh), peak_discharge_hour, peak_charge_hour (local hour of the day, unit hour), round_trip_ratio "
            "(discharged over charged, a ratio of the day's energies as reported, not a measured efficiency).",
        ]
        path = os.path.join(ip.OUT_DIR, NAME + ".csv")
        with open(path + ".tmp", "w", encoding="utf-8", newline="") as f:
            for h in header + [f"File holds {len(out)} rows, rewritten whole by this run."]:
                f.write("# " + h + "\n")
            out.to_csv(f, index=False, lineterminator="\n")
        os.replace(path + ".tmp", path)
        ip.update_sources([{"source": "erw:storage_daily_cycle", "publisher": "Energy Research Warehouse (ERW), derived",
                            "report": "Battery storage daily cycle (docs/methods/storage.md)", "report_url": METHOD_URL,
                            "document_list": "", "license": "public", "tables": [NAME]},
                           {"source": CAISO_SOURCE, "publisher": "Energy Research Warehouse (ERW), derived from California ISO",
                            "report": "Battery storage daily cycle, CAISO rows, from CAISO Today's Outlook "
                                      "(caiso_battery_storage; docs/methods/storage.md)",
                            "report_url": CAISO_METHOD_URL, "document_list": "", "license": "public", "tables": [NAME]}])
        status["detail"] = f"{len(out)} rows, {out['ts_utc'].nunique()} days; {len(caiso)} CAISO rows from {CAISO_INPUT}"
        print(f"{NAME}.csv: rows={len(out)}")
        log(status["detail"])
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"storage_daily_cycle FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        status.update(status="failed", detail=tb.strip().splitlines()[-1][:300])
    ip.write_status("storage_daily_cycle", run_id, [status])
    log.close()
    return 0 if status["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
