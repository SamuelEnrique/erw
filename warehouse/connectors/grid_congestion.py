#!/usr/bin/env python3
"""Congestion as the operators publish it: binding transmission constraints with their shadow prices, and the
congestion part of hub and zone prices. SPP and CAISO, day-ahead, hourly.

Energy Research Warehouse (ERW) connector, chain 601 session 9000 (docs/methods/grid_congestion.md). Writes two
series tables:

constraints_binding_hourly: one row a constraint that bound, an hour, a market
    entity    spp:<Constraint Name>|<Contingency Name>       the operator's own names, unchanged
              caiso:<NOMOGRAM_ID_XML>|<CONSTRAINT_CAUSE>      CAISO publishes one branch under more than one
                                                             contingency in the same hour, so the contingency is
                                                             part of the key, after a "|"
    variable  shadow_price_dam    the constraint's shadow price in the day-ahead market, USD/MWh, as published
                                  (SPP prints them negative; CAISO positive; neither sign is changed)
    x_constraint, x_contingency, x_monitored, x_contingent_facility, x_constraint_type, x_nerc_id, x_state:
              the columns of the operator's file, as printed (empty where the operator prints none)

price_congestion_hourly: the parts of the day-ahead price at each hub and zone the operator splits
    entity    spp:SPPNORTH_HUB, spp:SPPSOUTH_HUB; caiso:TH_NP15_GEN-APND, caiso:TH_SP15_GEN-APND,
              caiso:TH_ZP26_GEN-APND, caiso:DLAP_PGAE-APND, caiso:DLAP_SCE-APND, caiso:DLAP_SDGE-APND,
              caiso:DLAP_VEA-APND
    variable  lmp_dam, energy_dam, congestion_dam, loss_dam (SPP: LMP, MEC, MCC, MLC; CAISO: LMP, MCE, MCC, MCL),
              and for CAISO ghg_dam (MGHG) where it is printed. USD/MWh.

    python warehouse/connectors/grid_congestion.py --table constraints --operator spp --start 2026-01-01
    python warehouse/connectors/grid_congestion.py --table prices --operator caiso --start 2023-08-01
    python warehouse/connectors/grid_congestion.py --out-dir C:/scratch ...   # a trial: nothing in warehouse/output
    python warehouse/connectors/grid_congestion.py --offline ...              # from the raw files only

Sources
    SPP: the Marketplace portal's file browser (https://portal.spp.org), folders da-binding-constraints
    ("Day-Ahead Binding Constraints", one csv an operating day, DA-BC-<YYYYMMDD>0100.csv) and
    da-lmp-by-settlement-location ("Day-Ahead LMP by Settlement Location", DA-LMP-SL-<YYYYMMDD>0100.csv). A year SPP
    has archived is one zip (/<year>/<year>.zip); the connector asks the year's folder which it is. The price zips
    of archived years hold every settlement location and are not read by this connector (the year is reported as
    not pulled).
    CAISO: OASIS (https://oasis.caiso.com/oasisapi/SingleZip), PRC_NOMOGRAM version 1 with market_run_id=DAM
    ("Nomogram/Branch Shadow Prices"), and PRC_LMP version 12 with market_run_id=DAM ("Locational Marginal Prices"),
    one request a calendar month or less (OASIS answers at most 31 days), five seconds apart. OASIS keeps PRC_LMP
    for a rolling window (about 39 months); PRC_NOMOGRAM was found back to 2015.

Never fill. A constraint is a row only in an hour the operator lists it as binding; an hour it did not bind has no
row (absence is not a zero). A price day is written for a (place, part) only when every hour of the operating day is
there exactly once (24, or 23 and 25 at the clock changes). A document the source does not hold is a gap, logged.

Licenses: public, with citation. SPP's terms (https://www.spp.org/terms-conditions/): "Permission is implicitly
granted to copy and distribute (via computer network or printed form) in whole or in part (with appropriate
citation) EXCEPT when such materials will be used, in whole or in part, within a commercial publication"; a
commercial use needs SPP's written authorization. CAISO: "freely available for public use consistent with the
general policies of the Public Records Act" (docs/licenses.md, read #3). ERCOT is not asked: its reports are only on
the paths its robots file disallows (the owner's ruling 2 of 6 November 2026). PJM, NYISO and ISO-NE are held by
license and MISO is paused: none is asked.
"""

import argparse
import datetime as dt
import io
import json
import os
import sys
import time
import traceback
import zipfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "grid_congestion"
T_CONS = "constraints_binding_hourly"
T_PRICE = "price_congestion_hourly"
X_CONS = ["x_constraint", "x_contingency", "x_monitored", "x_contingent_facility", "x_constraint_type",
          "x_nerc_id", "x_state"]
COLS_CONS = ip.SERIES_COLS + X_CONS
KEY = ["entity", "variable", "ts_utc"]

SPP_TZ = "America/Chicago"
SPP_GEO = "US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY"
SPP_LIST = "https://portal.spp.org/file-browser-api/?fsName={fs}&path=/{year}&type=folder"
SPP_FILE = "https://portal.spp.org/file-browser-api/download/{fs}?path=/{path}"
SPP_BC = dict(fs="da-binding-constraints", prefix="DA-BC", source="spp:DA-BC",
              report="Day-Ahead Binding Constraints", page="https://portal.spp.org/pages/da-binding-constraints")
SPP_LMP = dict(fs="da-lmp-by-settlement-location", prefix="DA-LMP-SL", source="spp:DA-LMP-SL",
               report="Day-Ahead LMP by Settlement Location", page="https://portal.spp.org/pages/da-lmp-by-settlement-location")
SPP_HUBS = ["SPPNORTH_HUB", "SPPSOUTH_HUB"]
SPP_PARTS = {"LMP": "lmp_dam", "MEC": "energy_dam", "MCC": "congestion_dam", "MLC": "loss_dam"}

CAISO_TZ = "America/Los_Angeles"
CAISO_GEO = "US-CA,US-NV"
OASIS = "https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname={q}&version={v}&market_run_id=DAM{extra}&startdatetime={s}&enddatetime={e}"
OASIS_PAGE = "https://oasis.caiso.com/mrioasis/logon.do"
CAISO_NOMO = dict(q="PRC_NOMOGRAM", v=1, source="caiso:PRC_NOMOGRAM", report="OASIS Nomogram/Branch Shadow Prices, day-ahead market (DAM)")
CAISO_LMP = dict(q="PRC_LMP", v=12, source="caiso:PRC_LMP", report="OASIS Locational Marginal Prices, day-ahead market (DAM)")
CAISO_NODES = ["TH_NP15_GEN-APND", "TH_SP15_GEN-APND", "TH_ZP26_GEN-APND", "DLAP_PGAE-APND", "DLAP_SCE-APND",
               "DLAP_SDGE-APND", "DLAP_VEA-APND"]
CAISO_PARTS = {"LMP": "lmp_dam", "MCE": "energy_dam", "MCC": "congestion_dam", "MCL": "loss_dam", "MGHG": "ghg_dam"}
CAISO_FIRST = {"constraints": "2015-01-01", "prices": "2023-08-01"}
SPP_FIRST = {"constraints": "2014-03-01", "prices": "2025-01-01"}


# ---------------------------------------------------------------------------
# time
# ---------------------------------------------------------------------------

def day_hours(day, tz):
    """The UTC starts of every hour of a local operating day."""
    a = pd.Timestamp(day).tz_localize(tz)
    b = (pd.Timestamp(day) + pd.Timedelta(days=1)).tz_localize(tz)
    return list(pd.date_range(a.tz_convert("UTC"), b.tz_convert("UTC"), freq="1h", inclusive="left"))


def utc_text(ts):
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")


def stale(day):
    """A day within the last four days is fetched again (its file may still change)."""
    return pd.Timestamp(day) >= pd.Timestamp.now().normalize() - pd.Timedelta(days=4)


# ---------------------------------------------------------------------------
# SPP
# ---------------------------------------------------------------------------

def spp_archived(fs, year, log, offline):
    url = SPP_LIST.format(fs=fs, year=year)
    if offline:
        hit = ip.raw_cached(CONNECTOR, SPP_FILE.format(fs=fs, path=f"{year}/{year}.zip"))
        return hit is not None
    raw, _ = ip.fetch_raw(CONNECTOR, url, log, fresh=True)
    return any(x.get("name") == f"{year}.zip" for x in json.loads(raw.decode("utf-8")))


def spp_docs(feed, days, log, offline, allow_zip):
    """The documents that hold `days`: one zip for an archived year, else one file a day."""
    docs, skipped = [], []
    for year in sorted({d.year for d in days}, reverse=True):
        ydays = [d for d in days if d.year == year]
        if spp_archived(feed["fs"], year, log, offline):
            if allow_zip:
                docs.append(dict(url=SPP_FILE.format(fs=feed["fs"], path=f"{year}/{year}.zip"), year=year,
                                 days=ydays, fresh=False))
            else:
                skipped.append(f"SPP {feed['report']} {year}: archived as one zip of every settlement location; not read")
        else:
            for d in sorted(ydays, reverse=True):
                path = d.strftime(f"%Y/%m/By_Day/{feed['prefix']}-%Y%m%d0100.csv")
                docs.append(dict(url=SPP_FILE.format(fs=feed["fs"], path=path), days=[d], fresh=stale(d)))
    return docs, skipped


def spp_texts(raw, doc, feed, log, gaps):
    """(day, csv text) for each day the document holds."""
    if "year" not in doc:
        return [(doc["days"][0], raw.decode("utf-8-sig"))]
    z = zipfile.ZipFile(io.BytesIO(raw))
    names = {}
    for n in z.namelist():
        base = n.rsplit("/", 1)[-1]
        if base.startswith(feed["prefix"] + "-") and base.endswith(".csv"):
            names[base[len(feed["prefix"]) + 1:len(feed["prefix"]) + 9]] = n
    out = []
    for d in doc["days"]:
        n = names.get(d.strftime("%Y%m%d"))
        if n is None:
            gaps.append(f"SPP {feed['report']} {d.date()}: not in the {doc['year']} zip")
            continue
        out.append((d, z.read(n).decode("utf-8-sig")))
    return out


def spp_frame(text):
    x = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)
    # SPP's older files name the columns in capitals with underscores (GMTINTERVALEND, SETTLEMENT_LOCATION; seen in
    # DA-LMP-SL files of 2025); they are read as the newer names, nothing else changes
    upper = {"INTERVAL": "Interval", "GMTINTERVALEND": "GMTIntervalEnd", "SETTLEMENT_LOCATION": "Settlement Location",
             "PNODE": "Pnode", "CONSTRAINT_NAME": "Constraint Name", "CONSTRAINT_TYPE": "Constraint Type",
             "SHADOW_PRICE": "Shadow Price", "MONITORED_FACILITY": "Monitored Facility",
             "CONTINGENT_FACILITY": "Contingent Facility", "CONTINGENCY_NAME": "Contingency Name", "STATE": "State"}
    x.columns = [upper.get(c.strip(), c.strip()) for c in x.columns]
    for c in x.columns:
        x[c] = x[c].str.strip()
    if "GMTIntervalEnd" not in x.columns:
        raise RuntimeError(f"no GMTIntervalEnd column; columns {list(x.columns)}: layout changed")
    # some 2015 files end with rows whose every cell is empty (7,211 in the 2015 zip): no row; a row with any cell
    # filled and no time still fails the file
    x = x[(x != "").any(axis=1)]
    x["ts"] = spp_time(x["GMTIntervalEnd"]) - pd.Timedelta(hours=1)
    return x


def spp_time(s):
    """SPP's GMT interval ends: "11/18/2026 07:00:00" in most files, "11/1/2026 6:00" in some (seen 20 November 2026).
    Each form is read strictly; a value in neither form fails the file. A bare date ("6/15/2022", in the 2022 zip) is
    that day's midnight: the files that write it write every other hour with its time."""
    t = pd.to_datetime(s, format="%m/%d/%Y %H:%M:%S", errors="coerce").fillna(
        pd.to_datetime(s, format="%m/%d/%Y %H:%M", errors="coerce")).fillna(
        pd.to_datetime(s, format="%m/%d/%Y", errors="coerce"))
    if t.isna().any():
        raise RuntimeError(f"SPP time values in no known form: {s[t.isna()].head(3).tolist()}")
    return t.dt.tz_localize("UTC")


def spp_constraints(day, text, rec):
    x = spp_frame(text)
    if "Contingency Name" not in x.columns and day < pd.Timestamp("2022-01-01"):
        # the files before 2022 print no contingency name (seen in the 2021 zip): the key is the name alone there
        x["Contingency Name"] = ""
    need = ["Constraint Name", "Constraint Type", "NERCID", "State", "Shadow Price", "Monitored Facility",
            "Contingent Facility", "Contingency Name"]
    miss = [c for c in need if c not in x.columns]
    if miss:
        raise RuntimeError(f"SPP DA-BC {day.date()}: columns {miss} missing; columns {list(x.columns)}")
    hours = set(day_hours(day, SPP_TZ))
    if set(x["ts"]) - hours:
        raise RuntimeError(f"SPP DA-BC {day.date()}: hours outside the operating day")
    x = x[x["Shadow Price"] != ""]
    # session 9000: SPP's 2023 file prints one element twice, its two ends in each order (TMP831_29014 on 2023-11-08:
    # "LN VINETAP3 - NHAYS" and "LN NHAYS - VINETAP3"), same contingency, same shadow price. Such rows are one row,
    # naming both spellings; a repeat with a different shadow price fails the file.
    key = ["ts", "Constraint Name", "Contingency Name"]
    if x.duplicated(key).any():
        rep = x[x.duplicated(key, keep=False)]
        if (rep.groupby(key)["Shadow Price"].nunique() > 1).any():
            raise RuntimeError(f"SPP DA-BC {day.date()}: one constraint, contingency and hour with two shadow prices")
        mon = x.groupby(key)["Monitored Facility"].agg(lambda s: " / ".join(sorted(set(s))))
        x = x.drop_duplicates(key).set_index(key)
        x["Monitored Facility"] = mon
        x = x.reset_index()
    return pd.DataFrame({
        # session 9000: SPP's 2023 files list one constraint under two contingencies in an hour (TMP831_29014 on
        # 2023-11-08), so the contingency is part of the key for SPP as for CAISO
        "entity": "spp:" + x["Constraint Name"] + x["Contingency Name"].map(lambda c: f"|{c}" if c else ""), "variable": "shadow_price_dam", "ts_utc": x["ts"].map(utc_text),
        "value": pd.to_numeric(x["Shadow Price"], errors="raise"), "unit": "USD/MWh", "freq": "PT1H",
        "geo": SPP_GEO, "market": "spp_dam", "node": "", "source": SPP_BC["source"], "source_url": rec["url"],
        "retrieved_at": rec["retrieved_at"], "vintage": "",
        "x_constraint": x["Constraint Name"], "x_contingency": x["Contingency Name"],
        "x_monitored": x["Monitored Facility"], "x_contingent_facility": x["Contingent Facility"],
        "x_constraint_type": x["Constraint Type"], "x_nerc_id": x["NERCID"], "x_state": x["State"],
    })


def spp_prices(day, text, rec):
    x = spp_frame(text)
    loc = "Settlement Location" if "Settlement Location" in x.columns else "Settlement Location Name"
    if loc not in x.columns or any(c not in x.columns for c in SPP_PARTS):
        raise RuntimeError(f"SPP DA-LMP-SL {day.date()}: columns {list(x.columns)}: layout changed")
    x = x[x[loc].isin(SPP_HUBS)]
    out = []
    for col, var in SPP_PARTS.items():
        out.append(pd.DataFrame({"place": x[loc], "variable": var, "ts": x["ts"], "value": x[col]}))
    rows = pd.concat(out, ignore_index=True)
    rows = rows[rows["value"] != ""]
    rows["value"] = pd.to_numeric(rows["value"], errors="raise")
    return rows.assign(day=day, ns="spp", market="spp_dam", geo=SPP_GEO, source=SPP_LMP["source"],
                       source_url=rec["url"], retrieved_at=rec["retrieved_at"])


# ---------------------------------------------------------------------------
# CAISO OASIS
# ---------------------------------------------------------------------------

def oasis_months(days):
    """(first day, day after the last) for each calendar month the days touch, newest first."""
    out = []
    for (y, m), g in pd.Series(days).groupby([pd.Series(days).dt.year, pd.Series(days).dt.month]):
        out.append((min(g), max(g) + pd.Timedelta(days=1)))
    return sorted(out, reverse=True)


def oasis_url(feed, a, b, extra=""):
    s = pd.Timestamp(a).tz_localize(CAISO_TZ).tz_convert("UTC").strftime("%Y%m%dT%H:%M-0000")
    e = pd.Timestamp(b).tz_localize(CAISO_TZ).tz_convert("UTC").strftime("%Y%m%dT%H:%M-0000")
    return OASIS.format(q=feed["q"], v=feed["v"], extra=extra, s=s, e=e)


def oasis_frame(raw, url, gaps, label):
    z = zipfile.ZipFile(io.BytesIO(raw))
    csvs = [n for n in z.namelist() if n.lower().endswith(".csv")]
    if not csvs:
        xml = " ".join(z.read(n).decode("utf-8", "replace")[:600] for n in z.namelist())
        if "No data returned" in xml or "1000" in xml:
            gaps.append(f"CAISO {label}: OASIS returned no data ({url})")
            return None
        raise RuntimeError(f"OASIS answered without a csv for {url}: {xml[:400]}")
    return pd.concat([pd.read_csv(z.open(n), dtype=str, keep_default_na=False) for n in csvs], ignore_index=True)


def caiso_constraints(x, rec):
    need = ["INTERVALSTARTTIME_GMT", "NOMOGRAM_ID_XML", "CONSTRAINT_CAUSE", "PRC"]
    if any(c not in x.columns for c in need):
        raise RuntimeError(f"PRC_NOMOGRAM columns {list(x.columns)}: layout changed")
    for c in need:
        x[c] = x[c].str.strip()
    x = x.drop_duplicates(["INTERVALSTARTTIME_GMT", "NOMOGRAM_ID_XML", "CONSTRAINT_CAUSE", "PRC"])
    ts = pd.to_datetime(x["INTERVALSTARTTIME_GMT"], utc=True)
    return pd.DataFrame({
        "entity": "caiso:" + x["NOMOGRAM_ID_XML"] + "|" + x["CONSTRAINT_CAUSE"], "variable": "shadow_price_dam",
        "ts_utc": ts.map(utc_text), "value": pd.to_numeric(x["PRC"], errors="raise"), "unit": "USD/MWh",
        "freq": "PT1H", "geo": CAISO_GEO, "market": "caiso_dam", "node": "", "source": CAISO_NOMO["source"],
        "source_url": rec["url"], "retrieved_at": rec["retrieved_at"], "vintage": "",
        "x_constraint": x["NOMOGRAM_ID_XML"], "x_contingency": x["CONSTRAINT_CAUSE"], "x_monitored": "",
        "x_contingent_facility": "", "x_constraint_type": "", "x_nerc_id": "", "x_state": "",
    })


def caiso_prices(x, rec):
    need = ["INTERVALSTARTTIME_GMT", "NODE", "LMP_TYPE", "MW"]
    if any(c not in x.columns for c in need):
        raise RuntimeError(f"PRC_LMP columns {list(x.columns)}: layout changed")
    x = x[x["LMP_TYPE"].isin(CAISO_PARTS)]
    ts = pd.to_datetime(x["INTERVALSTARTTIME_GMT"], utc=True)
    day = ts.dt.tz_convert(CAISO_TZ).dt.tz_localize(None).dt.normalize()
    return pd.DataFrame({
        "place": x["NODE"].str.strip(), "variable": x["LMP_TYPE"].map(CAISO_PARTS), "ts": ts,
        "value": pd.to_numeric(x["MW"], errors="raise"), "day": day,
    }).assign(ns="caiso", market="caiso_dam", geo=CAISO_GEO, source=CAISO_LMP["source"], source_url=rec["url"],
              retrieved_at=rec["retrieved_at"])


# ---------------------------------------------------------------------------
# complete days, writing
# ---------------------------------------------------------------------------

def complete_prices(rows, tz, log, gaps):
    if rows.duplicated(["place", "variable", "ts"]).any():
        d = rows[rows.duplicated(["place", "variable", "ts"], keep=False)].iloc[0]
        raise RuntimeError(f"price rows repeat a (place, part, hour): {d['place']} {d['variable']} {d['ts']}")
    keep = []
    for (day, place, var), g in rows.groupby(["day", "place", "variable"], sort=True):
        hours = set(day_hours(day, tz))
        if len(g) == len(hours) and set(g["ts"]) == hours:
            keep.append(g)
        else:
            gaps.append(f"{place} {var} {pd.Timestamp(day).date()}: {len(g)} of {len(hours)} hours, left out")
    return pd.concat(keep, ignore_index=True) if keep else rows.iloc[0:0]


def price_series(rows):
    return pd.DataFrame({
        "entity": rows["ns"] + ":" + rows["place"], "variable": rows["variable"], "ts_utc": rows["ts"].map(utc_text),
        "value": rows["value"], "unit": "USD/MWh", "freq": "PT1H", "geo": rows["geo"], "market": rows["market"],
        "node": rows["place"], "source": rows["source"], "source_url": rows["source_url"],
        "retrieved_at": rows["retrieved_at"], "vintage": "",
    })[ip.SERIES_COLS]


def write(name, new, cols, header, log, keep_since=None):
    """Merge new rows into the table by (entity, variable, ts_utc). keep_since: a rolling table drops rows before this
    UTC time (caiso_tie_flows_5min keeps 35 days); the count dropped is in the file's last header line."""
    path = os.path.join(ip.OUT_DIR, name + ".csv")
    ip._require_lock(path, f"writing {name}")
    old = ip.read_series(path, cols) if os.path.exists(path) else None
    merged, st = ip.merge_series(old, new[cols], KEY, cols)
    dropped = 0
    if keep_since is not None:
        n0 = len(merged)
        merged = merged[merged["ts_utc"] >= keep_since]
        dropped = n0 - len(merged)
        header = list(header) + [f"Rolling: rows before {keep_since} are dropped; this run dropped {dropped}."]
    merged = merged.sort_values(["market", "ts_utc", "entity", "variable"]).reset_index(drop=True)
    by_market = "; ".join(f"{m}: {len(g)} rows, {g['ts_utc'].min()} to {g['ts_utc'].max()}, "
                          f"{g['entity'].nunique()} entities" for m, g in merged.groupby("market"))
    lines = list(header) + [
        f"File holds {len(merged)} rows, {merged['ts_utc'].min()} to {merged['ts_utc'].max()} ({by_market}). This run "
        f"wrote {len(new)} rows: {st['added']} new, {st['replaced']} replacing earlier rows with the same "
        f"(entity, variable, ts_utc); {st['kept']} rows are kept from earlier runs. Per row, source, source_url and "
        "retrieved_at say where it came from; earlier run logs are in warehouse/output/logs/."]
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        for line in lines:
            f.write("# " + line + "\n")
        merged.to_csv(f, index=False, lineterminator="\n")
    os.replace(tmp, path)
    msg = f"{name}.csv: rows={len(merged)} (this run {len(new)}: {st['added']} new, {st['replaced']} replaced, {st['kept']} kept); {by_market}"
    print(msg)
    log("  " + msg)


LICENSE_LINE = ("License: public, with citation. SPP's terms (https://www.spp.org/terms-conditions/): \"Permission is "
                "implicitly granted to copy and distribute (via computer network or printed form) in whole or in part "
                "(with appropriate citation) EXCEPT when such materials will be used, in whole or in part, within a "
                "commercial publication\"; CAISO: \"freely available for public use consistent with the general "
                "policies of the Public Records Act\" (credit the California ISO).")
NOT_ASKED = ("Not asked: ERCOT (its reports are only on the paths its robots file disallows; the owner's ruling 2 of 6 "
             "November 2026), PJM (paid license), NYISO and ISO-NE (written permission), MISO (paused since 4 October "
             "2026).")


def header_cons(run_id, gaps, sources):
    return [
        "Energy Research Warehouse (ERW): binding transmission constraints and their shadow prices, day-ahead, hourly "
        "(SPP and CAISO)",
        "Shape: series (docs/datastandard.md v0). One row a constraint that bound in an hour: an hour it did not bind "
        "has no row. value is the shadow price in USD/MWh as the operator prints it (SPP's are negative, CAISO's "
        "positive; no sign is changed). ts_utc is the start of the hour, UTC.",
        "entity: spp:<Constraint Name>|<Contingency Name>; caiso:<NOMOGRAM_ID_XML>|<CONSTRAINT_CAUSE> (each operator lists one constraint under more "
        "than one contingency in an hour). The x_ columns repeat the operator's own columns; no constraint is placed "
        "on a map.",
        NOT_ASKED,
        f"Gaps in this run: {len(gaps)}" + (": " + "; ".join(gaps[:25]) if gaps else "") + ".",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/{CONNECTOR}.py",
        f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
        f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git; each run's manifest.csv lists each file and URL)",
        "Source: " + "; ".join(sources),
        LICENSE_LINE,
        "Method: docs/methods/grid_congestion.md",
    ]


def header_price(run_id, gaps, sources):
    return [
        "Energy Research Warehouse (ERW): the parts of the day-ahead price at hubs and zones, hourly (SPP and CAISO)",
        "Shape: series (docs/datastandard.md v0). USD/MWh. lmp_dam = energy_dam + congestion_dam + loss_dam (+ "
        "ghg_dam at CAISO), as each operator publishes the split; nothing here is computed. ts_utc is the start of "
        "the hour, UTC.",
        "Places: SPP SPPNORTH_HUB, SPPSOUTH_HUB; CAISO TH_NP15_GEN-APND, TH_SP15_GEN-APND, TH_ZP26_GEN-APND, "
        "DLAP_PGAE-APND, DLAP_SCE-APND, DLAP_SDGE-APND, DLAP_VEA-APND. A (place, part, day) is written only when "
        "every hour of the operating day is there.",
        NOT_ASKED,
        f"Gaps in this run: {len(gaps)}" + (": " + "; ".join(gaps[:25]) if gaps else "") + ".",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/{CONNECTOR}.py",
        f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
        f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git; each run's manifest.csv lists each file and URL)",
        "Source: " + "; ".join(sources),
        LICENSE_LINE,
        "Method: docs/methods/grid_congestion.md",
    ]


# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------

def pull(table, operator, start, until, log, offline, gaps):
    """Rows for one table and operator, newest documents first."""
    first = (SPP_FIRST if operator == "spp" else CAISO_FIRST)[table]
    a = max(pd.Timestamp(start), pd.Timestamp(first))
    days = list(pd.date_range(a, pd.Timestamp(until) - pd.Timedelta(days=1), freq="D"))
    if not days:
        return None, None
    frames, t0 = [], time.time()
    if operator == "spp":
        feed = SPP_BC if table == "constraints" else SPP_LMP
        docs, skipped = spp_docs(feed, days, log, offline, allow_zip=(table == "constraints"))
        gaps += skipped
        for i, doc in enumerate(docs):
            try:
                raw, rec = ip.fetch_raw(CONNECTOR, doc["url"], log, offline=offline, fresh=doc["fresh"])
            except ip.SourceGap as exc:
                gaps.append(f"SPP {feed['report']} {doc['days'][0].date()}: not at the source")
                log(f"  gap: {exc}")
                continue
            for day, text in spp_texts(raw, doc, feed, log, gaps):
                frames.append(spp_constraints(day, text, rec) if table == "constraints" else spp_prices(day, text, rec))
            if not rec.get("cached"):
                time.sleep(1)
            if i % 25 == 0:
                print(f"{CONNECTOR} spp {table}: {i + 1} of {len(docs)} documents, {time.time() - t0:.0f} s", flush=True)
        src = (feed["source"], feed["report"], feed["page"])
    else:
        feed = CAISO_NOMO if table == "constraints" else CAISO_LMP
        extra = "" if table == "constraints" else "&node=" + ",".join(CAISO_NODES)
        months = oasis_months(days)
        for i, (m0, m1) in enumerate(months):
            url = oasis_url(feed, m0, m1, extra)
            fresh = stale(m1 - pd.Timedelta(days=1))
            raw, rec = ip.fetch_raw(CONNECTOR, url, log, offline=offline, fresh=fresh)
            x = oasis_frame(raw, url, gaps, f"{feed['q']} {m0.date()} to {(m1 - pd.Timedelta(days=1)).date()}")
            if x is not None:
                frames.append(caiso_constraints(x, rec) if table == "constraints" else caiso_prices(x, rec))
            if not rec.get("cached"):
                time.sleep(5)
            print(f"{CONNECTOR} caiso {table}: {i + 1} of {len(months)} months, {time.time() - t0:.0f} s", flush=True)
        src = (feed["source"], feed["report"], OASIS_PAGE)
    if not frames:
        return None, src
    rows = pd.concat(frames, ignore_index=True)
    if table == "prices":
        tz = SPP_TZ if operator == "spp" else CAISO_TZ
        rows = rows[(rows["day"] >= a) & (rows["day"] < pd.Timestamp(until))]
        rows = price_series(complete_prices(rows, tz, log, gaps))
    if rows.duplicated(KEY).any():
        d = rows[rows.duplicated(KEY, keep=False)].head(2)
        raise RuntimeError(f"{table} {operator}: rows repeat a key: {d[KEY].values.tolist()}")
    return rows, src


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: binding constraints and the congestion part of price (SPP, CAISO)")
    ap.add_argument("--table", choices=["constraints", "prices", "all"], default="all")
    ap.add_argument("--operator", choices=["spp", "caiso", "all"], default="all")
    ap.add_argument("--start", default="2026-01-01", help="first operating day (default 2026-01-01)")
    ap.add_argument("--until", help="first operating day not pulled (default: tomorrow)")
    ap.add_argument("--out-dir")
    ap.add_argument("--offline", action="store_true")
    a = ap.parse_args(argv)
    raw_dir = ip.RAW_DIR
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    until = a.until or str((pd.Timestamp.now().normalize() + pd.Timedelta(days=1)).date())
    tables = ["constraints", "prices"] if a.table == "all" else [a.table]
    operators = ["spp", "caiso"] if a.operator == "all" else [a.operator]
    results = []
    for table in tables:
        name = T_CONS if table == "constraints" else T_PRICE
        frames, gaps, sources, regs = [], [], [], []
        try:
            for op in operators:
                if ip.paused(op):
                    log(f"{op}: {ip.pause_line(op)}")
                    continue
                rows, src = pull(table, op, a.start, until, log, a.offline, gaps)
                if src:
                    sources.append(f"{src[0]} {src[1]}, {src[2]}")
                    regs.append(dict(source=src[0], publisher=ip.ISO_PUBLISHERS[op], report=src[1], report_url=src[2],
                                     document_list=src[2], license="public", tables=[name]))
                if rows is not None and len(rows):
                    frames.append(rows)
                    log(f"{name} {op}: {len(rows)} rows, {rows['ts_utc'].min()} to {rows['ts_utc'].max()}")
            if not frames:
                raise RuntimeError("no row was read; nothing written")
            new = pd.concat(frames, ignore_index=True)
            for g in gaps:
                log(f"  gap: {g}")
            cols = COLS_CONS if table == "constraints" else ip.SERIES_COLS
            hdr = (header_cons if table == "constraints" else header_price)(run_id, gaps, sources)
            write(name, new, cols, hdr, log)
            ip.update_sources(regs)
            results.append(dict(table=name, market="DAM", status="ok", detail=f"{len(new)} rows"))
            results += [dict(table=name, market="DAM", status="gap", detail=g[:300]) for g in gaps]
        except Exception:
            tb = ip.redact(traceback.format_exc())
            last = tb.strip().splitlines()[-1]
            log(f"{name} FAILED, no output file written:\n{tb}")
            print(f"{CONNECTOR} {name} FAILED, no output file written: {last}", file=sys.stderr)
            results.append(dict(table=name, market="DAM", status="failed", detail=last[:300]))
    ip.write_status(CONNECTOR, run_id, results)
    failures = sum(r["status"] == "failed" for r in results)
    log(f"done, failures={failures}")
    log.close()
    print(f"{CONNECTOR} run log: {os.path.relpath(log.path, ip.ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
