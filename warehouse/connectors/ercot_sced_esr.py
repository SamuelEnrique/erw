#!/usr/bin/env python3
"""ERCOT's 60-Day SCED Disclosure, the Energy Storage Resource file: what each storage resource did in real time
(session 120).

    python warehouse/connectors/ercot_sced_esr.py --list                      # ERCOT's file list (one request), measured
    python warehouse/connectors/ercot_sced_esr.py --pull --from 2026-02-01    # ask ERCOT, a day at a time; reduce as read
    python warehouse/connectors/ercot_sced_esr.py --pull --offline --from 2026-02-01   # the saved zips only; no request
    python warehouse/connectors/ercot_sced_esr.py --write                     # the table, from the days (data lock)

Energy Research Warehouse (ERW). Table: ercot_sced_esr_hourly, a series table, one row per Energy Storage Resource,
hour and variable (method docs/methods/ercot_storage_realtime.md).

The source. ERCOT posts a "60-Day SCED Disclosure Reports" zip (report type 13052) each day, for the operating day 60
days before. Since the market change of 5 December 2025 (real-time co-optimization, one model for a battery) a zip is
about 56 MB and holds, among eleven files:

  60d_ESR_Data_in_SCED-DD-MMM-YY.csv   a row for each Energy Storage Resource and each SCED run (about every five
      minutes; 98,310 rows on 5 August 2026): its limits, its status, its Base Point (what SCED told it to do), its
      Telemetered Net Output, its State of Charge, its real-time awards of each Ancillary Service, and its offer curves
      (160 of its 198 columns, not read here);
  60d_SCED_SMNE_GEN_RES-DD-MMM-YY.csv  the settlement metered net energy of each resource by 15-minute interval.

An approved pull (session 120): the storage resources' rows from 6 December 2025, USD 0, ceilings of 12 GB of
downloads and 9,000,000 stored rows in total (with the node prices pulled beside it). Measured first, on ERCOT's list
of 5 October 2026: the 243 days from 6 December 2025 are 13.4 GB, which passes the ceiling, so the pull takes the most
recent months that fit, 1 February to 5 August 2026 (186 days, 10.4 GB), and says so wherever its figures are shown.
The rules it keeps:

- one zip at a time, a pause between requests;
- a zip is saved once, under warehouse/raw/ercot_60d_sced/zips/ with a line in manifest.csv, and never asked for twice;
- each day is reduced to resource-hour totals as it is read (this machine has 8 GB: a day's storage file is 100 MB of
  text) and written to warehouse/raw/ercot_60d_sced/days/<day>.csv before the next zip is asked for; the zip is kept;
- before a request that would pass the download ceiling the run stops and says so;
- nothing is filled: a day whose zip is not there, has no storage file, or fails a check is a missing day, named in
  warehouse/raw/ercot_60d_sced/days/missing.csv with its reason, and has no rows. An hour of a resource with no SCED
  run in it has no row;
- ERCOT stamps a run in Central prevailing time. The stamps are read to UTC before anything is measured, so the day
  the clocks go forward is 23 hours of five-minute runs and not a 65-minute gap (the first version of this reducer
  refused 8 March 2026 for that gap). A day with a repeated hour (the autumn change) is left out with its reason: no
  such day has been seen, and a rule that was never run on one is not trusted with one.

What an hour's row is (reduce_day):

  runs                      the SCED runs in the hour that hold the resource
  net_output_mwh            its Telemetered Net Output integrated over the hour: each run's MW held until the next SCED
                            run of the day, whichever resources that run holds (the last run of the day until midnight),
                            positive when it discharges. A resource that a run does not hold has no energy for that
                            run: nothing is carried across it. Telemetry, not the settlement meter
  net_q1_mwh ... net_q4_mwh the same for each of the hour's four 15-minute Settlement Intervals (ERCOT settles real-time
                            energy by the interval: Protocols 6.6.3.1), so that a row is still a resource and an hour
                            and an interval's energy can still be set beside that interval's price. They add up to
                            net_output_mwh
  discharge_mwh, charge_mwh the same, the positive part and the negative part (charge as a positive number)
  base_point_mwh            the Base Point integrated the same way: what SCED instructed
  hsl_mw, lsl_mw            the hour's highest High Sustained Limit and lowest Low Sustained Limit
  soc_start_mwh, soc_min_mwh, soc_max_mwh   the State of Charge at the hour's first run, and its range in the hour
  as_<product>_mwh          each Ancillary Service's real-time award integrated over the hour (a MW for an hour):
                            regup, regdn, rrspfr, rrsffr, rrsufr, ecrs, nspin
  metered_mwh               the settlement metered net energy of the hour's four 15-minute intervals, when the SMNE
                            file holds the resource for all four (written only then)
"""
import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import os
import re
import sys
import time
import zipfile

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

TABLE = "ercot_sced_esr_hourly"
REPORT_TYPE = 13052
SOURCE = "ercot:NP3-965-ER"
PAGE = "https://www.ercot.com/mp/data-products/data-product-details?id=NP3-965-ER"
LIST = f"https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId={REPORT_TYPE}"
FILE = "https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId={doc}"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
LAG_DAYS = 60
REGULAR = "60_Day_SCED_Disclosure"   # the daily zip's FriendlyName; corrections and supplements carry other names
MAX_BYTES = 12_000_000_000           # the approved ceiling on downloads, with the node prices pulled beside this
MAX_ROWS = 9_000_000                 # the approved ceiling on stored rows, in all
PAUSE = 2.0
TZ = "America/Chicago"
RAW = os.path.join(ROOT, "warehouse", "raw", "ercot_60d_sced")
ZIPS = os.path.join(RAW, "zips")
DAYS = os.path.join(RAW, "days")
MANIFEST = os.path.join(ZIPS, "manifest.csv")
MANIFEST_COLS = ["operating_day", "file", "doc_id", "url", "bytes", "sha256", "published", "retrieved_at", "how"]
MISSING = os.path.join(DAYS, "missing.csv")
AS = {"AS Awards REGUP": "as_regup_mwh", "AS Awards REGDN": "as_regdn_mwh", "AS Awards RRSPFR": "as_rrspfr_mwh", "AS Awards RRSFFR": "as_rrsffr_mwh",
      "AS Awards RRSUFR": "as_rrsufr_mwh", "AS Awards ECRS": "as_ecrs_mwh", "AS Awards NSPIN": "as_nspin_mwh"}
KEEP = ["SCED Time Stamp", "Repeated Hour Flag", "QSE", "Resource Name", "Resource Type", "HSL", "LSL", "Telemetered Resource Status", "Base Point",
        "Telemetered Net Output", "State of Charge"] + list(AS)
QUARTERS = ["net_q1_mwh", "net_q2_mwh", "net_q3_mwh", "net_q4_mwh"]
DAY_COLS = ["resource", "qse", "hour", "runs", "net_output_mwh"] + QUARTERS + ["discharge_mwh", "charge_mwh", "base_point_mwh", "hsl_mw", "lsl_mw",
                                                                             "soc_start_mwh", "soc_min_mwh", "soc_max_mwh"] + list(AS.values()) + ["metered_mwh"]


class Ceiling(RuntimeError):
    """A ceiling of the approved pull would be passed: the run stops and reports."""


def operating_day(doc):
    """The operating day a posted zip holds: the day it was published less 60."""
    return dt.date.fromisoformat(doc["PublishDate"][:10]) - dt.timedelta(days=LAG_DAYS)


def manifest():
    if not os.path.exists(MANIFEST):
        return []
    with open(MANIFEST, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def manifest_add(row):
    os.makedirs(ZIPS, exist_ok=True)
    new = not os.path.exists(MANIFEST)
    with open(MANIFEST, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=MANIFEST_COLS, lineterminator="\n")
        if new:
            w.writeheader()
        w.writerow(row)


def downloaded_bytes():
    """The bytes this connector has asked ERCOT for, every run together: the ceiling is on their sum."""
    return sum(int(r["bytes"]) for r in manifest() if r["how"] == "requested")


def get_zip(doc, day, log, offline, state, get=requests.get):
    """(the zip's path, its url, when it was retrieved) for one listed document; from the disk when it is held. None
    when the machine holds no copy and the run is offline. Raises Ceiling before a request that would pass 12 GB."""
    name, url = doc["ConstructedName"], FILE.format(doc=doc["DocID"])
    path = os.path.join(ZIPS, name)
    if os.path.exists(path):
        got = {r["file"]: r for r in manifest()}.get(name)
        return path, url, got["retrieved_at"] if got else dt.datetime.fromtimestamp(os.path.getmtime(path), dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if offline:
        return None
    size = int(doc["ContentSize"])
    if state["bytes"] + size > MAX_BYTES:
        raise Ceiling(f"{day}: its zip of {size:,} bytes would pass the download ceiling of {MAX_BYTES:,} (at {state['bytes']:,})")
    if state["requests"]:
        time.sleep(PAUSE)
    last = None
    for attempt in range(4):
        try:
            g = get(url, headers=UA, timeout=600)
            state["requests"] += 1
            if g.status_code == 200 and len(g.content) == size:
                break
            last = f"HTTP {g.status_code}, {len(g.content):,} bytes of {size:,}"
        except requests.RequestException as e:
            state["requests"] += 1
            last = f"{type(e).__name__}: {str(e)[:120]}"
        log(f"  {day}: attempt {attempt + 1} failed ({last})")
        time.sleep(15 * (attempt + 1))
    else:
        raise IOError(f"four attempts failed, the last: {last}")
    when = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    os.makedirs(ZIPS, exist_ok=True)
    with open(path + ".tmp", "wb") as f:
        f.write(g.content)
    os.replace(path + ".tmp", path)
    state["bytes"] += len(g.content)
    manifest_add({"operating_day": day.isoformat(), "file": name, "doc_id": doc["DocID"], "url": url, "bytes": len(g.content),
                  "sha256": hashlib.sha256(g.content).hexdigest(), "published": doc["PublishDate"], "retrieved_at": when, "how": "requested"})
    return path, url, when


def read_files(path):
    """The two files of one disclosure zip this connector reads: (the storage file's name, its rows with the columns of
    KEEP, the metered file's rows or None). Every value a string as ERCOT prints it. Raises ValueError when the zip
    holds no storage file (or more than one), or the file lacks a column."""
    z = zipfile.ZipFile(path)
    names = [n for n in z.namelist() if re.search(r"60d_ESR_Data_in_SCED", n)]
    if len(names) != 1:
        raise ValueError(f"the zip holds {len(names)} storage files among its {len(z.namelist())} files")
    with z.open(names[0]) as f:
        head = pd.read_csv(f, nrows=0).columns
    cols = [c.strip() for c in head]
    missing = [c for c in KEEP if c not in cols]
    if missing:
        raise ValueError(f"{names[0]} lacks the columns {missing}")
    with z.open(names[0]) as f:
        df = pd.read_csv(f, dtype=str, keep_default_na=False, na_values=[], usecols=[h for h in head if h.strip() in KEEP])
    df.columns = [c.strip() for c in df.columns]
    smne = None
    ms = [n for n in z.namelist() if re.search(r"60d_SCED_SMNE_GEN_RES", n)]
    if len(ms) == 1:
        with z.open(ms[0]) as f:
            smne = pd.read_csv(f, dtype=str, keep_default_na=False, na_values=[])
        smne.columns = [c.strip() for c in smne.columns]
    return names[0], df, smne


def num(s):
    return pd.to_numeric(s.replace("", pd.NA), errors="coerce")


def reduce_day(df, smne, day):
    """One day's storage file as resource-hour totals (DAY_COLS). Every check that fails raises ValueError: the day is
    then missing. df: the rows of KEEP as strings; smne: the metered file's rows or None; day: the operating day."""
    if df.empty:
        raise ValueError("the storage file has no rows")
    kinds = set(df["Resource Type"])
    if kinds != {"ESR"}:
        raise ValueError(f"resource types {sorted(kinds)}, not ESR alone")
    t = pd.to_datetime(df["SCED Time Stamp"], format="%m/%d/%Y %H:%M:%S", errors="coerce")
    if t.isna().any():
        raise ValueError(f"{int(t.isna().sum())} SCED time stamps cannot be read")
    if set(t.dt.date) != {day}:
        raise ValueError(f"the file's days are {sorted(str(d) for d in set(t.dt.date))[:3]}, not {day}")
    rep = df["Repeated Hour Flag"].str.upper()
    if not set(rep) <= {"N", "Y"}:
        raise ValueError(f"Repeated Hour Flag holds {sorted(set(rep))[:4]}")
    if (rep == "Y").any():
        raise ValueError("a repeated hour (the autumn clock change): the day is not reduced")
    # ERCOT's stamps are Central prevailing time: to UTC, so that a clock change is not a gap. A stamp the change makes
    # ambiguous or absent cannot be placed and stops the day
    t = t.dt.tz_localize(TZ, ambiguous="NaT", nonexistent="NaT").dt.tz_convert("UTC")
    if t.isna().any():
        raise ValueError(f"{int(t.isna().sum())} SCED time stamps fall in an hour the clock change makes ambiguous or absent")
    d = pd.DataFrame({"resource": df["Resource Name"], "qse": df["QSE"], "t": t, "out": num(df["Telemetered Net Output"]), "bp": num(df["Base Point"]),
                      "hsl": num(df["HSL"]), "lsl": num(df["LSL"]), "soc": num(df["State of Charge"])})
    for src, name in AS.items():
        d[name] = num(df[src]).fillna(0.0)   # a blank award is no award: zero MW in that run
    if d.duplicated(["resource", "t"]).any():
        raise ValueError(f"{int(d.duplicated(['resource', 't']).sum())} rows repeat a resource and a SCED time stamp")
    d = d.sort_values(["resource", "t"]).reset_index(drop=True)
    # the SCED clock of the day: every run's stamp, whichever resources it holds. A run's values hold until the next run
    # on that clock (the day's last run until local midnight). A resource a run does not hold has no row for it, and so
    # no energy: its last values are never carried across a run it was not in (on 5 February 2026 one resource is in
    # the file until 00:30 and not after; held to its own next row, its last five minutes would have been 23 hours)
    end = (pd.Timestamp(day) + pd.Timedelta(days=1)).tz_localize(TZ).tz_convert("UTC")
    clock = sorted(d["t"].unique())
    after = dict(zip(clock, clock[1:] + [end]))
    nxt = d["t"].map(after)
    gap = pd.Series(clock[1:] + [end]) - pd.Series(clock)
    if (gap > pd.Timedelta(hours=1)).any():
        i = int(gap.idxmax())
        raise ValueError(f"a gap of {gap.max().total_seconds() / 60:.0f} minutes between SCED runs (after {clock[i]})")
    # a run is cut at each quarter-hour it crosses (runs come about every five minutes, so most are one piece and some
    # two; the gap check above allows at most four cuts), so that an interval's energy is the energy of that interval
    q15 = pd.Timedelta(minutes=15)
    first_q = d["t"].dt.floor("15min")
    pieces = []
    for k in range(5):
        start = pd.concat([d["t"], first_q + k * q15], axis=1).max(axis=1)
        stop = pd.concat([nxt, first_q + (k + 1) * q15], axis=1).min(axis=1)
        h = (stop - start).dt.total_seconds() / 3600.0
        pieces.append(d.assign(quarter=first_q + k * q15, h=h)[h > 0])
    p = pd.concat(pieces, ignore_index=True)
    p = p[p["quarter"] < end]
    if abs(p["h"].sum() - (nxt - d["t"]).dt.total_seconds().sum() / 3600.0) > 1e-6:
        raise ValueError("the pieces of the SCED runs do not add up to the time they cover")
    p["hour"] = p["quarter"].dt.floor("h")
    val = {"net_output_mwh": p["out"] * p["h"], "discharge_mwh": p["out"].clip(lower=0) * p["h"], "charge_mwh": (-p["out"]).clip(lower=0) * p["h"],
           "base_point_mwh": p["bp"] * p["h"]}
    for name in AS.values():
        val[name] = p[name] * p["h"]
    qn = ((p["quarter"] - p["hour"]) / q15).round().astype(int)
    for i, name in enumerate(QUARTERS):
        val[name] = (p["out"] * p["h"]).where(qn == i, 0.0)
    e = pd.DataFrame(val).assign(resource=p["resource"], hour=p["hour"])   # by p's own index: .values would drop the time zone
    out = e.groupby(["resource", "hour"]).sum(min_count=1)
    g = d.assign(hour=d["t"].dt.floor("h")).groupby(["resource", "hour"])
    out["runs"] = g.size()
    out["qse"] = g["qse"].first()
    out["hsl_mw"], out["lsl_mw"] = g["hsl"].max(), g["lsl"].min()
    out["soc_start_mwh"], out["soc_min_mwh"], out["soc_max_mwh"] = g["soc"].first(), g["soc"].min(), g["soc"].max()
    out = out[out["runs"].notna()]   # an hour reached only by the tail of the hour before has no run of its own: no row
    out["metered_mwh"] = pd.NA
    if smne is not None and len(smne):
        mt = pd.to_datetime(smne["Interval Time"], format="%m/%d/%Y %H:%M:%S", errors="coerce")
        mt = (mt - pd.Timedelta(seconds=1)).dt.tz_localize(TZ, ambiguous="NaT", nonexistent="NaT").dt.tz_convert("UTC")
        m = pd.DataFrame({"resource": smne["Resource Code"], "hour": mt.dt.floor("h"), "v": num(smne["Interval Value"])})
        m = m[m["resource"].isin(set(d["resource"])) & m["hour"].notna()]
        mg = m.groupby(["resource", "hour"])["v"].agg(["sum", "count"])
        out["metered_mwh"] = mg.loc[mg["count"] == 4, "sum"].reindex(out.index)
    out = out.reset_index()
    out["runs"] = out["runs"].astype(int)
    out["hour"] = out["hour"].dt.strftime("%Y-%m-%dT%H:00:00Z")   # the hour's start, UTC
    return out[DAY_COLS].sort_values(["resource", "hour"]).reset_index(drop=True)


def day_path(day):
    return os.path.join(DAYS, f"{day}.csv")


def record_missing(day, reason):
    os.makedirs(DAYS, exist_ok=True)
    new = not os.path.exists(MISSING)
    with open(MISSING, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        if new:
            w.writerow(["operating_day", "reason", "recorded_at"])
        w.writerow([day, reason, dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")])


def listing(log, get=requests.get, offline=False):
    """ERCOT's list of the report's zips: the regular daily ones by operating day, and everything else by name."""
    saved = os.path.join(RAW, "doclist_latest.json")
    if offline:
        text = open(saved, encoding="utf-8").read()
    else:
        if ip.paused("ercot"):
            raise RuntimeError("ERCOT is paused (warehouse/metadata/paused_sources.csv): nothing is requested")
        last = None
        for attempt in range(4):
            try:
                r = get(LIST, headers=UA, timeout=120)
                r.raise_for_status()
                text = r.text
                break
            except requests.RequestException as e:
                last = e
                time.sleep(15)
        else:
            raise IOError(f"the list could not be read: {last}")
        os.makedirs(RAW, exist_ok=True)
        with open(saved, "w", encoding="utf-8") as f:
            f.write(text)
    docs = [d["Document"] for d in json.loads(text)["ListDocsByRptTypeRes"]["DocumentList"]]
    regular = {}
    for d in docs:
        if d["FriendlyName"] == REGULAR:
            day = operating_day(d)
            if day in regular:
                raise ValueError(f"two regular zips for {day}")
            regular[day] = d
    other = [d for d in docs if d["FriendlyName"] != REGULAR]
    log(f"ERCOT lists {len(docs)} zips of report {REPORT_TYPE}: {len(regular)} regular, operating days {min(regular)} to {max(regular)}, "
        f"{sum(int(d['ContentSize']) for d in regular.values()):,} bytes; {len(other)} corrections and supplements")
    return regular, other


def pull(a, log):
    regular, _ = listing(log, offline=a.offline)
    first = dt.date.fromisoformat(a.from_day)
    last = dt.date.fromisoformat(a.to_day) if a.to_day else max(regular)
    want = [d for d in sorted(regular) if first <= d <= last]
    need = sum(int(regular[d]["ContentSize"]) for d in want if not os.path.exists(os.path.join(ZIPS, regular[d]["ConstructedName"])))
    state = {"bytes": downloaded_bytes(), "requests": 0}
    log(f"{len(want)} operating days wanted, {first} to {last}; {need:,} bytes not yet on this machine; downloaded so far {state['bytes']:,} of {MAX_BYTES:,}")
    if state["bytes"] + need > MAX_BYTES and not a.offline:
        raise Ceiling(f"the days wanted need {need:,} more bytes, which with {state['bytes']:,} already downloaded passes {MAX_BYTES:,}: ask for fewer days")
    os.makedirs(DAYS, exist_ok=True)
    done = rows = 0
    for day in want:
        if os.path.exists(day_path(day)) and not a.again:
            done += 1
            continue
        try:
            got = get_zip(regular[day], day, log, a.offline, state)
            if got is None:
                log(f"  {day}: not on this machine, and the run is offline")
                continue
            name, df, smne = read_files(got[0])
            out = reduce_day(df, smne, day)
        except Ceiling:
            raise
        except (ValueError, IOError, zipfile.BadZipFile, KeyError) as e:
            log(f"  {day}: MISSING: {e}")
            record_missing(day, str(e)[:300])
            continue
        with open(day_path(day) + ".tmp", "w", encoding="utf-8", newline="") as f:
            f.write(f"# {name} in {regular[day]['ConstructedName']}; {FILE.format(doc=regular[day]['DocID'])}; retrieved {got[2]}\n")
            out.to_csv(f, index=False, lineterminator="\n")
        os.replace(day_path(day) + ".tmp", day_path(day))
        done += 1
        rows += len(out)
        log(f"  {day}: {len(df):,} rows of {out['resource'].nunique()} resources -> {len(out):,} resource-hours "
            f"({int(out['metered_mwh'].notna().sum()):,} with all four metered intervals); downloaded {state['bytes']:,}")
    log(f"{done} of {len(want)} days reduced under {os.path.relpath(DAYS, ROOT)}; {rows:,} resource-hours written by this run; "
        f"{state['requests']} requests, {state['bytes']:,} bytes downloaded in all")
    return 0


X = {"qse": "x_qse", "runs": "x_sced_runs", "net_q1_mwh": "x_net_q1_mwh", "net_q2_mwh": "x_net_q2_mwh", "net_q3_mwh": "x_net_q3_mwh", "net_q4_mwh": "x_net_q4_mwh",
     "discharge_mwh": "x_discharge_mwh", "charge_mwh": "x_charge_mwh", "base_point_mwh": "x_base_point_mwh", "hsl_mw": "x_hsl_mw", "lsl_mw": "x_lsl_mw",
     "soc_start_mwh": "x_soc_start_mwh", "soc_min_mwh": "x_soc_min_mwh", "soc_max_mwh": "x_soc_max_mwh", "as_regup_mwh": "x_as_regup_mwh",
     "as_regdn_mwh": "x_as_regdn_mwh", "as_rrspfr_mwh": "x_as_rrspfr_mwh", "as_rrsffr_mwh": "x_as_rrsffr_mwh", "as_rrsufr_mwh": "x_as_rrsufr_mwh",
     "as_ecrs_mwh": "x_as_ecrs_mwh", "as_nspin_mwh": "x_as_nspin_mwh"}
COLS = ip.SERIES_COLS + list(X.values())
ESR_TABLE = "ercot_dam_esr_awards"   # where a resource's settlement point is read from: ERCOT's SCED file does not name it


def day_frames(days_dir=None):
    """Every reduced day on this machine, oldest first: (day, its first line, its frame)."""
    import glob
    for p in sorted(glob.glob(os.path.join(days_dir or DAYS, "20??-??-??.csv"))):
        with open(p, encoding="utf-8") as f:
            head = f.readline().lstrip("# ").strip()
        yield os.path.basename(p)[:10], head, pd.read_csv(p, comment="#", dtype={"resource": str, "qse": str, "hour": str})


def settlement_points(out_dir=None):
    """{resource: its settlement point} from the day-ahead awards table, where ERCOT prints it; {} when that table is
    not on the machine. A resource with more than one point in that table keeps its newest."""
    path = os.path.join(out_dir or ip.OUT_DIR, ESR_TABLE + ".csv")
    if not os.path.exists(path):
        return {}
    d = pd.read_csv(path, skiprows=ip.header_rows(path), usecols=["entity", "ts_utc", "node"], dtype=str, keep_default_na=False)
    d = d[d["node"] != ""].sort_values("ts_utc").drop_duplicates("entity", keep="last")
    return dict(zip(d["entity"].str[len("ercot:"):], d["node"]))


def to_rows(day, head, df, points):
    """One reduced day in the table's shape. The reduced day's hour is the hour's start in UTC."""
    utc = pd.to_datetime(df["hour"], utc=True)
    m = re.search(r"; (https://\S+); retrieved (\S+)", head)
    url, when = (m.group(1), m.group(2)) if m else (PAGE, "")
    fmt = lambda s: s.map(lambda v: "" if pd.isna(v) else format(float(v), ".6f").rstrip("0").rstrip("."))  # noqa: E731
    out = pd.DataFrame({"entity": "ercot:" + df["resource"], "variable": "net_output_mwh", "ts_utc": utc.dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "value": fmt(df["net_output_mwh"]), "unit": "MWh", "freq": "PT1H", "geo": "US-TX", "market": "ercot_rtm",
                        "node": df["resource"].map(points).fillna(""), "source": SOURCE, "source_url": url, "retrieved_at": when,
                        "vintage": (dt.date.fromisoformat(day) + dt.timedelta(days=LAG_DAYS)).isoformat() + "T00:00:00Z"})
    for src, dst in X.items():
        out[dst] = df[src] if src == "qse" else (df[src].astype(int).astype(str) if src == "runs" else fmt(df[src]))
    return out[COLS]


def write(log, run_id):
    """The table, from the days reduced by --pull, a day at a time."""
    points = settlement_points()
    path = os.path.join(ip.OUT_DIR, TABLE + ".csv")
    ip._require_lock(path, f"writing {TABLE}")
    tmp, n, days, without_point = path + ".tmp", 0, [], set()
    with open(tmp + ".rows", "w", encoding="utf-8", newline="") as body:
        for day, head, df in day_frames():
            rows = to_rows(day, head, df, points)
            without_point |= set(rows.loc[rows["node"] == "", "entity"])
            if n + len(rows) > MAX_ROWS:
                body.close()
                os.remove(tmp + ".rows")
                raise SystemExit(f"{day}: its rows would pass the ceiling of {MAX_ROWS:,}; nothing written")
            rows.to_csv(body, index=False, header=False, lineterminator="\n")
            n += len(rows)
            days.append(day)
    if not days:
        os.remove(tmp + ".rows")
        raise SystemExit("no day has been reduced; nothing written")
    missing = []
    if os.path.exists(MISSING):
        with open(MISSING, encoding="utf-8", newline="") as f:
            missing = [r for r in csv.DictReader(f) if days[0] <= r["operating_day"] <= days[-1] and r["operating_day"] not in days]
    span = pd.date_range(days[0], days[-1]).strftime("%Y-%m-%d")
    absent = [d for d in span if d not in days]
    lines = [
        "Energy Research Warehouse (ERW): ERCOT Energy Storage Resources in real time, by resource and hour, from ERCOT's 60-Day SCED Disclosure Reports, "
        "the file 60d_ESR_Data_in_SCED, each day reduced to resource-hour totals as it was read (session 120)",
        "Shape: series (docs/datastandard.md v0, Decision 40), one row per resource and hour: entity ercot:<Resource Name>, variable net_output_mwh, value the "
        "resource's Telemetered Net Output integrated over the hour (MWh; positive is discharge; each SCED run's MW held until the resource's next run), ts_utc the "
        "hour's start, node its settlement point as the day-ahead disclosure names it (blank when that file never names the resource). The x_ columns: "
        "x_net_q1_mwh to x_net_q4_mwh, the same for each 15-minute Settlement Interval of the hour (they add up to the value); x_discharge_mwh and x_charge_mwh, the "
        "positive and the negative part (charge as a positive number); x_base_point_mwh, the Base Point integrated the same way; x_hsl_mw and x_lsl_mw, the hour's "
        "highest High Sustained Limit and lowest Low Sustained Limit; x_soc_start_mwh, x_soc_min_mwh, x_soc_max_mwh, the State of Charge; x_as_<service>_mwh, each "
        "Ancillary Service's real-time award integrated over the hour (a MW for an hour): regup, regdn, rrspfr, rrsffr, rrsufr, ecrs, nspin; x_sced_runs, the SCED "
        "runs in the hour; x_qse, the scheduling entity.",
        "What it is not: telemetry, not the settlement meter (ERCOT's metered file in the same zip does not hold the storage resources). No price is in ERCOT's "
        "file and none is in this table. The offer curves (160 of the file's 198 columns) are left out.",
        f"Operating days held: {len(days)}, {days[0]} to {days[-1]} (local, Central). Days absent between them: {len(absent)}"
        + (": " + "; ".join(absent[:20]) if absent else "") + (f". Days that failed a check: " + "; ".join(f"{m['operating_day']} ({m['reason'][:80]})" for m in missing) if missing else "")
        + ". Nothing is filled for a day or an hour that is not there.",
        "The pull took the most recent months that fit its ceiling: from 6 December 2025 ERCOT lists 13.4 GB of these zips, above the approved 12 GB, so it "
        "begins on 1 February 2026.",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/ercot_sced_esr.py; each row's retrieved_at is when its zip was downloaded, vintage the day ERCOT published it "
        "(the operating day plus 60 days), source_url the zip. The zips are kept under warehouse/raw/ercot_60d_sced/zips/ with a manifest.",
        f"Run log: warehouse/raw/ercot_60d_sced/pull_{run_id}.log",
        f"Source: {SOURCE} ERCOT, 60-Day SCED Disclosure Reports (report type {REPORT_TYPE}), {PAGE}; document list {LIST}",
        "License: public. ERCOT's terms of use (https://www.ercot.com/help/terms): raw data in public portions of the website may be used, reproduced and redistributed "
        "in compilations, charts and analyses.",
        f"File holds {n:,} rows; the approved ceiling is {MAX_ROWS:,} stored rows in all. {len(without_point)} resources have no settlement point in {ESR_TABLE}.",
    ]
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        for line in lines:
            f.write("# " + line + "\n")
        f.write(",".join(COLS) + "\n")
        with open(tmp + ".rows", encoding="utf-8", newline="") as body:
            for line in body:
                f.write(line)
    os.remove(tmp + ".rows")
    os.replace(tmp, path)
    ip.update_sources([dict(source=SOURCE, publisher=ip.ISO_PUBLISHERS["ercot"], report="60-Day SCED Disclosure Reports (the file 60d_ESR_Data_in_SCED: Energy Storage Resources in real time)",
                            report_url=PAGE, document_list=LIST, license="public", tables=[TABLE])])
    ip.write_status("ercot_sced_esr", run_id, [{"table": TABLE, "status": "ok", "rows": n, "detail": f"{len(days)} operating days {days[0]} to {days[-1]}; {len(absent)} absent"}])
    line = f"{TABLE}.csv: rows={n:,} days={len(days)} ({days[0]}..{days[-1]}) absent={len(absent)}"
    print(line)
    log("  " + line)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERCOT 60-Day SCED Disclosure, the storage file (session 120)")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--pull", action="store_true")
    ap.add_argument("--write", action="store_true", help="the table, from the reduced days (the data lock)")
    ap.add_argument("--offline", action="store_true", help="the saved zips only; no request")
    ap.add_argument("--from", dest="from_day", default="2026-02-01")
    ap.add_argument("--to", dest="to_day")
    ap.add_argument("--again", action="store_true", help="reduce a day again though its file is there (the zip is read from the disk)")
    a = ap.parse_args(argv)
    os.makedirs(RAW, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    logf = open(os.path.join(RAW, f"pull_{run_id}.log"), "a", encoding="utf-8")

    def log(m):
        print(m, flush=True)
        logf.write(m + "\n")
        logf.flush()
    try:
        if a.list:
            listing(log, offline=a.offline)
            return 0
        if a.pull:
            return pull(a, log)
        if a.write:
            return write(log, run_id)
        ap.error("--list, --pull or --write")
    except Ceiling as e:
        log(f"STOPPED at a ceiling: {e}")
        return 3
    finally:
        logf.close()


if __name__ == "__main__":
    sys.exit(main())
