#!/usr/bin/env python3
"""ERCOT's 60-Day DAM Disclosure, the Energy Storage Resource file: what each storage resource was awarded day-ahead
(session 115).

    python warehouse/connectors/ercot_dam_esr.py --pull --from 2025-12-05          # ask ERCOT, a month at a time
    python warehouse/connectors/ercot_dam_esr.py --pull --days 2025-12-04          # named operating days only (a probe)
    python warehouse/connectors/ercot_dam_esr.py --pull --offline --from 2025-12-05  # the saved zips only; no request
    python warehouse/connectors/ercot_dam_esr.py --write                           # the table, from the months (data lock)
    python warehouse/connectors/ercot_dam_esr.py --daily                           # the standing pull: one zip, the next day

Energy Research Warehouse (ERW). Table: ercot_dam_esr_awards, a series table, one row per Energy Storage Resource and
hour (docs/datastandard.md, Decision 40; method docs/methods/ercot_storage_dam_awards.md).

The source. ERCOT posts a "60-Day DAM Disclosure Reports" zip (EMIL NP3-966-ER, report type 13051) each day, for the
operating day 60 days before. One file in it, 60d_DAM_ESR_Data-DD-MMM-YY.csv, has a row for each Energy Storage
Resource and hour ending: its limits (HSL, LSL), its status, its awarded energy and the price at its own settlement
point, and its award and the clearing price (MCPC) of each Ancillary Service. A file cannot be had without its zip.

An approved pull (session 115): the ESR file only, every day it exists, USD 0, ceilings of 9,000,000 rows and 3 GB of
downloads. The rules it keeps:

- one zip at a time, a pause between requests;
- a zip is saved once, under warehouse/raw/ercot_60d_dam/zips/ with a line in manifest.csv, and never asked for twice:
  a zip already held (there, or in a session 108 run folder beside it) is read from the disk;
- a month is read, checked and written (warehouse/raw/ercot_60d_dam/months/) before the next begins;
- before a request that would pass the download ceiling, and before a day whose rows would pass the row ceiling, the
  run stops and says so. Nothing partial is written for the month it stopped in;
- nothing is filled: a day whose zip is not there, has no ESR file, or fails a check is a missing day, named in the
  month's record with its reason, and has no rows.

Values are written as ERCOT prints them (strings, not re-rounded). A blank award is no award and stays blank.

The standing pull (session 116, approved: one zip a day in the daily run, under warehouse/health.py, started by
warehouse/scheduled.py ercot_storage_dam). --daily asks ERCOT for its list and then for one zip at most: the first
listed operating day after the last day the table holds. Its rows are added to the end of the table, which must be on
the machine (the runner restores it from the Redivis draft); then the monthly awards table and the offers tables
(warehouse/derived/ercot_storage_dam_offers.py --days <day>) are built from it. One zip a run, the oldest first, so no
day is skipped: after a run that did not happen the table is a day further behind until a person approves a second
zip. A day that fails a check gets no rows and a line in warehouse/metadata/ercot_dam_esr_missing_days.csv, and the
next run goes on to the day after it. The 3 GB ceiling above was session 115's pull; a daily zip is not counted
against it, and a zip above 60 MB (they are 7 to 11) is not requested.
"""
import argparse
import csv
import datetime as dt
import glob
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

TABLE = "ercot_dam_esr_awards"
REPORT_TYPE = 13051
SOURCE = "ercot:NP3-966-ER"
PAGE = "https://www.ercot.com/mp/data-products/data-product-details?id=NP3-966-ER"
LIST = f"https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId={REPORT_TYPE}"
FILE = "https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId={doc}"
TERMS = "https://www.ercot.com/help/terms"
TERMS_QUOTE = ("The publicly available contents of this website may be used, reproduced, and redistributed, provided that the contents are not modified and that you "
               "maintain all copyright and other notices contained in the contents, including this Agreement. Notwithstanding the foregoing, raw data provided in public "
               "portions of this website may be used, reproduced, and redistributed in compilations, charts, and analyses without maintaining such notices.")
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
LAG_DAYS = 60
MAX_ROWS = 9_000_000          # the approved ceiling, in rows of ERCOT's file (a resource and hour)
MAX_BYTES = 3_000_000_000     # the approved ceiling on downloads, 3 GB
PAUSE = 2.0                   # seconds between requests
TZ = "America/Chicago"
RAW = os.path.join(ROOT, "warehouse", "raw", "ercot_60d_dam")
ZIPS = os.path.join(RAW, "zips")      # not a run id, so warehouse/prune_raw.py leaves it alone
MONTHS = os.path.join(RAW, "months")
MANIFEST = os.path.join(ZIPS, "manifest.csv")
MANIFEST_COLS = ["operating_day", "file", "doc_id", "url", "bytes", "sha256", "published", "retrieved_at", "how"]
DAILY_MAX_BYTES = 60_000_000  # the standing pull: one zip a run, and not one larger than this (they are 7 to 11 MB)
MISSING_DAYS = os.path.join(ROOT, "warehouse", "metadata", "ercot_dam_esr_missing_days.csv")  # tracked: days that failed a check
MONTHLY_BUILDER = os.path.join(ROOT, "warehouse", "derived", "ercot_storage_dam_awards.py")
OFFERS_BUILDER = os.path.join(ROOT, "warehouse", "derived", "ercot_storage_dam_offers.py")

# ERCOT's column -> the table's column. HSL is the row's value; the rest are x_ columns, as ERCOT gives them.
X = {"QSE": "x_qse", "DME": "x_dme", "Resource Status": "x_resource_status", "LSL": "x_lsl_mw",
     "Awarded Quantity": "x_energy_award_mw", "Energy Settlement Point Price": "x_energy_price_usd_per_mwh",
     "RegUp Awarded": "x_regup_award_mw", "RegUp MCPC": "x_regup_mcpc", "RegDown Awarded": "x_regdn_award_mw", "RegDown MCPC": "x_regdn_mcpc",
     "RRSPFR Awarded": "x_rrspfr_award_mw", "RRSFFR Awarded": "x_rrsffr_award_mw", "RRSUFR Awarded": "x_rrsufr_award_mw", "RRS MCPC": "x_rrs_mcpc",
     "ECRSSD Awarded": "x_ecrs_award_mw", "ECRS MCPC": "x_ecrs_mcpc", "NonSpin Awarded": "x_nonspin_award_mw", "NonSpin MCPC": "x_nonspin_mcpc"}
KEEP = ["Delivery Date", "Hour Ending", "Resource Name", "Resource Type", "HSL", "Settlement Point Name"] + list(X)
NUMERIC = ["HSL", "LSL", "Awarded Quantity", "Energy Settlement Point Price", "RegUp Awarded", "RegUp MCPC", "RegDown Awarded", "RegDown MCPC", "RRSPFR Awarded",
           "RRSFFR Awarded", "RRSUFR Awarded", "RRS MCPC", "ECRSSD Awarded", "ECRS MCPC", "NonSpin Awarded", "NonSpin MCPC"]
COLS = ip.SERIES_COLS + list(X.values())


class Ceiling(RuntimeError):
    """A ceiling of the approved pull would be passed: the run stops and reports."""


def operating_day(doc):
    """The operating day a posted zip holds: the day it was published less 60."""
    return dt.date.fromisoformat(doc["PublishDate"][:10]) - dt.timedelta(days=LAG_DAYS)


def read_esr(content):
    """The ESR file of one disclosure zip, every value a string as ERCOT prints it: (the file's name, its rows).

    Raises ValueError when the zip holds no ESR data file (or more than one), or the file lacks a column."""
    z = zipfile.ZipFile(io.BytesIO(content))
    names = [n for n in z.namelist() if re.search(r"60d_DAM_ESR_Data", n)]
    if len(names) != 1:
        raise ValueError(f"the zip holds {len(names)} ESR data files among its {len(z.namelist())} files")
    df = pd.read_csv(io.BytesIO(z.read(names[0])), dtype=str, keep_default_na=False, na_values=[])
    df.columns = [c.strip() for c in df.columns]
    missing = [c for c in KEEP if c not in df.columns]
    if missing:
        raise ValueError(f"{names[0]} lacks the columns {missing}")
    return names[0], df[KEEP].copy()


def to_rows(df, day, url, retrieved_at, vintage):
    """One day's ESR file in the table's shape. Every check that fails raises ValueError: the day is then missing."""
    for c in df.columns:
        df[c] = df[c].str.strip()
    dates = sorted(set(df["Delivery Date"]))
    if len(dates) != 1 or dt.datetime.strptime(dates[0], "%m/%d/%Y").date() != day:
        raise ValueError(f"the file's delivery dates are {dates}, not {day}")
    if (df["HSL"] == "").any():
        raise ValueError(f"{int((df['HSL'] == '').sum())} rows have no HSL")
    for c in NUMERIC:
        bad = pd.to_numeric(df[c].where(df[c] != ""), errors="coerce").isna() & (df[c] != "")
        if bad.any():
            raise ValueError(f"{c} holds values that are not numbers: {sorted(set(df.loc[bad, c]))[:5]}")
    he = pd.to_numeric(df["Hour Ending"], errors="raise")
    if not he.between(1, 24).all() or (he != he.round()).any():
        raise ValueError(f"hour ending outside 1 to 24: {sorted(set(df['Hour Ending']))[:30]}")
    # the hour's start, local, to UTC. A local hour that does not exist or happens twice raises: never guessed
    local = pd.to_datetime(day.isoformat()) + pd.to_timedelta(he - 1, unit="h")
    try:
        utc = local.dt.tz_localize(TZ, ambiguous="raise", nonexistent="raise").dt.tz_convert("UTC")
    except Exception as e:
        raise ValueError(f"an hour that the clock change makes ambiguous or absent: {e}")
    out = pd.DataFrame({
        "entity": "ercot:" + df["Resource Name"], "variable": "hsl_mw", "ts_utc": utc.dt.strftime("%Y-%m-%dT%H:%M:%SZ"), "value": df["HSL"],
        "unit": "MW", "freq": "PT1H", "geo": "US-TX", "market": "ercot_dam", "node": df["Settlement Point Name"], "source": SOURCE, "source_url": url,
        "retrieved_at": retrieved_at, "vintage": vintage})
    for src, dst in X.items():
        out[dst] = df[src]
    if (df["Resource Name"] == "").any():
        raise ValueError("a row has no resource name")
    if out.duplicated(["entity", "ts_utc"]).any():
        raise ValueError(f"{int(out.duplicated(['entity', 'ts_utc']).sum())} rows repeat a resource and hour")
    return out[COLS].sort_values(["entity", "ts_utc"]).reset_index(drop=True)


def manifest():
    if not os.path.exists(MANIFEST):
        return []
    with open(MANIFEST, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def manifest_add(row):
    new = not os.path.exists(MANIFEST)
    with open(MANIFEST, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=MANIFEST_COLS, lineterminator="\n")
        if new:
            w.writeheader()
        w.writerow(row)


def held_zips():
    """Every disclosure zip on this machine, by its name: the zips folder, and any earlier run's folder beside it."""
    out = {}
    for p in glob.glob(os.path.join(RAW, "*", "*.zip")):
        out.setdefault(os.path.basename(p), p)
    for p in glob.glob(os.path.join(ZIPS, "*.zip")):
        out[os.path.basename(p)] = p
    return out


def downloaded_bytes():
    """The bytes this connector has asked ERCOT for, every run together: the ceiling is on their sum."""
    return sum(int(r["bytes"]) for r in manifest() if r["how"] == "requested")


def get_zip(doc, day, log, offline, state):
    """(the zip's bytes, its url, when it was retrieved) for one listed document; from the disk when it is held.

    None when the machine holds no copy and the run is offline. Raises Ceiling before a request that would pass 3 GB."""
    name, url = doc["ConstructedName"], FILE.format(doc=doc["DocID"])
    held = held_zips()
    if name in held:
        path = held[name]
        got = {r["file"]: r for r in manifest()}.get(name)
        if got is None:  # a zip an earlier session saved: recorded once, with the time it was written
            when = dt.datetime.fromtimestamp(os.path.getmtime(path), dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            with open(path, "rb") as f:
                content = f.read()
            manifest_add({"operating_day": day.isoformat(), "file": name, "doc_id": doc["DocID"], "url": url, "bytes": len(content),
                          "sha256": hashlib.sha256(content).hexdigest(), "published": doc["PublishDate"], "retrieved_at": when,
                          "how": "held from " + os.path.relpath(os.path.dirname(path), RAW).replace(os.sep, "/")})
            return content, url, when
        with open(path, "rb") as f:
            return f.read(), url, got["retrieved_at"]
    if offline:
        return None
    size = int(doc["ContentSize"])
    if state["bytes"] + size > MAX_BYTES:
        raise Ceiling(f"{day}: its zip of {size:,} bytes would pass the download ceiling of {MAX_BYTES:,} (at {state['bytes']:,})")
    if state["requests"]:
        time.sleep(PAUSE)
    last = None
    for attempt in range(3):
        try:
            g = requests.get(url, headers=UA, timeout=300)
            state["requests"] += 1
            if g.status_code == 200 and len(g.content) == size:
                break
            last = f"HTTP {g.status_code}, {len(g.content):,} bytes of {size:,}"
        except requests.RequestException as e:
            state["requests"] += 1
            last = f"{type(e).__name__}: {e}"
        log(f"  {day}: attempt {attempt + 1} failed ({last})")
        time.sleep(10 * (attempt + 1))
    else:
        raise IOError(f"three attempts failed, the last: {last}")
    when = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    os.makedirs(ZIPS, exist_ok=True)
    path = os.path.join(ZIPS, name)
    with open(path + ".tmp", "wb") as f:
        f.write(g.content)
    os.replace(path + ".tmp", path)
    state["bytes"] += len(g.content)
    manifest_add({"operating_day": day.isoformat(), "file": name, "doc_id": doc["DocID"], "url": url, "bytes": len(g.content),
                  "sha256": hashlib.sha256(g.content).hexdigest(), "published": doc["PublishDate"], "retrieved_at": when, "how": "requested"})
    return g.content, url, when


def month_paths(month):
    return os.path.join(MONTHS, f"{TABLE}_{month}.csv"), os.path.join(MONTHS, f"{TABLE}_{month}.json")


def do_month(month, days, by_day, log, offline, state):
    """One month: each day's zip, its ESR rows checked, and the month written. Returns its record."""
    frames, held, missing = [], [], []
    for day in days:
        doc = by_day.get(day)
        if doc is None:
            missing.append({"day": day.isoformat(), "reason": "ERCOT's list holds no zip for this operating day"})
            continue
        try:
            got = get_zip(doc, day, log, offline, state)
        except Ceiling:
            raise
        except Exception as e:
            missing.append({"day": day.isoformat(), "reason": f"the zip could not be had: {e}"})
            log(f"  {day}: MISSING, the zip could not be had: {e}")
            continue
        if got is None:
            missing.append({"day": day.isoformat(), "reason": "no zip on this machine (offline run)"})
            continue
        content, url, when = got
        try:
            name, df = read_esr(content)
            rows = to_rows(df, day, url, when, ip.utc_iso(pd.Timestamp(doc["PublishDate"])))
        except ValueError as e:
            missing.append({"day": day.isoformat(), "reason": str(e)})
            log(f"  {day}: MISSING, {e}")
            continue
        if state["rows"] + len(rows) > MAX_ROWS:
            raise Ceiling(f"{day}: its {len(rows):,} rows would pass the row ceiling of {MAX_ROWS:,} (at {state['rows']:,})")
        state["rows"] += len(rows)
        frames.append(rows)
        held.append({"day": day.isoformat(), "file": name, "rows": int(len(rows)), "resources": int(rows["entity"].nunique()), "doc_id": doc["DocID"], "zip_bytes": len(content)})
        log(f"  {day}: {name}, {len(rows):,} rows, {rows['entity'].nunique()} resources")
    rec = {"month": month, "days_held": held, "days_missing": missing, "rows": int(sum(len(f) for f in frames))}
    os.makedirs(MONTHS, exist_ok=True)
    csv_path, json_path = month_paths(month)
    if frames:
        t = pd.concat(frames, ignore_index=True)
        if t.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError(f"{month}: the month's days repeat a resource and hour")
        t.to_csv(csv_path + ".tmp", index=False, lineterminator="\n")
        os.replace(csv_path + ".tmp", csv_path)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1)
    line = f"{month}: {len(held)} days held, {len(missing)} missing, {rec['rows']:,} rows; downloads so far {state['bytes']:,} bytes in {state['requests']} requests"
    print(line, flush=True)
    log(line)
    return rec


def pull(a, log):
    offline = a.offline
    state = {"bytes": downloaded_bytes(), "requests": 0, "rows": 0}
    list_path = os.path.join(RAW, "doclist_latest.json")
    if offline:
        if not os.path.exists(list_path):
            raise SystemExit("offline, and no saved file list: nothing to read")
        with open(list_path, encoding="utf-8") as f:
            text = f.read()
    else:
        if ip.paused("ercot"):
            raise SystemExit(ip.pause_line("ercot"))
        r = requests.get(LIST, headers=UA, timeout=120)
        state["requests"] += 1
        r.raise_for_status()
        text = r.text
        os.makedirs(RAW, exist_ok=True)
        with open(list_path, "w", encoding="utf-8") as f:
            f.write(text)
    docs = [x["Document"] for x in json.loads(text)["ListDocsByRptTypeRes"]["DocumentList"]]
    by_day = {}
    for d in sorted(docs, key=lambda d: d["PublishDate"]):
        by_day[operating_day(d)] = d  # a day posted twice: the later posting
    listed = sorted(by_day)
    log(f"{LIST}: {len(docs)} documents, operating days {listed[0]} to {listed[-1]}, {sum(int(d['ContentSize']) for d in docs):,} bytes listed")
    if a.days:
        days = sorted(dt.date.fromisoformat(x) for x in a.days.split(","))
    else:
        first = dt.date.fromisoformat(a.from_day) if a.from_day else listed[0]
        last = dt.date.fromisoformat(a.to_day) if a.to_day else listed[-1]
        days = [first + dt.timedelta(days=i) for i in range((last - first).days + 1)]
    # the plan, before any request: what would be downloaded, against the ceiling
    held = held_zips()
    to_get = [by_day[d] for d in days if d in by_day and by_day[d]["ConstructedName"] not in held]
    plan = sum(int(d["ContentSize"]) for d in to_get)
    line = (f"plan: {len(days)} operating days {days[0]} to {days[-1]}; {len(days) - len(to_get)} zips held or not listed, {len(to_get)} to request, {plan:,} bytes; "
            f"already requested by this connector {state['bytes']:,}; ceiling {MAX_BYTES:,}")
    print(line, flush=True)
    log(line)
    if not offline and state["bytes"] + plan > MAX_BYTES:
        raise Ceiling(f"the plan would pass the download ceiling: {state['bytes']:,} + {plan:,} > {MAX_BYTES:,}. Nothing requested")
    months = {}
    for d in days:
        months.setdefault(d.strftime("%Y-%m"), []).append(d)
    if a.days:  # a probe of named days: read and report, write no month
        for d in days:
            content, url, when = get_zip(by_day[d], d, log, offline, state)
            z = zipfile.ZipFile(io.BytesIO(content))
            esr = [n for n in z.namelist() if "ESR" in n.upper()]
            line = f"probe {d}: {len(content):,} bytes, {len(z.namelist())} files, ESR files: {esr or 'none'}; files: {sorted(z.namelist())}"
            print(line, flush=True)
            log(line)
        return 0
    for month in sorted(months):
        do_month(month, months[month], by_day, log, offline, state)
    line = f"pull done: {state['rows']:,} rows of a ceiling of {MAX_ROWS:,}; {state['bytes']:,} bytes requested of {MAX_BYTES:,}; {state['requests']} requests this run"
    print(line, flush=True)
    log(line)
    return 0


def write(log, run_id):
    """The table, from the months written by --pull, a month at a time (never the whole table in memory)."""
    recs = []
    for p in sorted(glob.glob(os.path.join(MONTHS, f"{TABLE}_*.json"))):
        with open(p, encoding="utf-8") as f:
            recs.append(json.load(f))
    recs = [r for r in recs if r["rows"]]
    if not recs:
        raise SystemExit("no month has been pulled; nothing written")
    held = [d for r in recs for d in r["days_held"]]
    missing = [d for r in recs for d in r["days_missing"]]
    rows = sum(r["rows"] for r in recs)
    if rows > MAX_ROWS:
        raise SystemExit(f"{rows:,} rows pass the ceiling of {MAX_ROWS:,}; nothing written")
    man = manifest()
    path = os.path.join(ip.OUT_DIR, TABLE + ".csv")
    ip._require_lock(path, f"writing {TABLE}")
    first, last = min(d["day"] for d in held), max(d["day"] for d in held)
    if os.path.exists(path) and last_day_held(path).isoformat() > last:
        # the standing pull adds days to the table itself; the months are rebuilt from the saved zips, with no request
        raise SystemExit(f"the table holds days to {last_day_held(path)} and the months only to {last}: nothing written. "
                         f"First: --pull --offline --from {last[:8]}01")
    lines = [
        "Energy Research Warehouse (ERW): ERCOT Energy Storage Resources' day-ahead awards, by resource and hour, from ERCOT's 60-Day DAM Disclosure Reports "
        "(NP3-966-ER), the file 60d_DAM_ESR_Data (session 115)",
        "Shape: series (docs/datastandard.md v0, Decision 40), one row per resource and hour: entity ercot:<Resource Name>, variable hsl_mw, value the resource's High "
        "Sustained Limit that hour (MW), ts_utc the hour's start (ERCOT gives the hour ending in Central prevailing time), node its settlement point. The awards are the x_ "
        "columns, as ERCOT prints them: x_energy_award_mw (Awarded Quantity; negative is a purchase, charging) and x_energy_price_usd_per_mwh (Energy Settlement Point "
        "Price, at the resource's own settlement point); for each Ancillary Service its award (MW) and its MCPC (USD per MW per hour): regup, regdn, rrs (three kinds of "
        "award, PFR, FFR and UFR, one price), ecrs, nonspin; x_lsl_mw (the Low Sustained Limit, negative: charging), x_resource_status, x_qse (the scheduling entity) and "
        "x_dme. A blank award is no award and stays blank. The offer curve columns of ERCOT's file are left out.",
        "What it is not: day-ahead awards only. No real-time settlement, no deployment energy, no contracts. It is not what any battery earned.",
        f"Operating days held: {len(held)}, {first} to {last} (local, Central). Days missing between them: {len(missing)}"
        + (": " + "; ".join(f"{m['day']} ({m['reason']})" for m in missing) if missing else "") + ". Nothing is filled for a missing day.",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/ercot_dam_esr.py; each row's retrieved_at is when its zip was downloaded, vintage when ERCOT published it "
        f"(the operating day plus 60 days), source_url the zip. {len(man)} zips in warehouse/raw/ercot_60d_dam/zips/manifest.csv.",
        f"Run log: warehouse/output/logs/{os.path.basename(log.path)}",
        f"Source: {SOURCE} ERCOT, 60-Day DAM Disclosure Reports, {PAGE}; document list {LIST}",
        f"License: public. ERCOT's terms ({TERMS}): \"{TERMS_QUOTE}\"",
        f"File holds {rows:,} rows of a ceiling of {MAX_ROWS:,} (the approved pull).",
    ]
    tmp = path + ".tmp"
    n = 0
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        for line in lines:
            f.write("# " + line + "\n")
        f.write(",".join(COLS) + "\n")
        for r in recs:
            with open(month_paths(r["month"])[0], encoding="utf-8", newline="") as m:
                head = m.readline().rstrip("\n").rstrip("\r")
                if head.split(",") != COLS:
                    raise RuntimeError(f"{r['month']}: the month's columns are not the table's")
                for line in m:
                    f.write(line)
                    n += 1
    if n != rows:
        os.remove(tmp)
        raise RuntimeError(f"the months hold {n:,} rows, their records say {rows:,}; nothing written")
    os.replace(tmp, path)
    ip.update_sources([dict(source=SOURCE, publisher=ip.ISO_PUBLISHERS["ercot"], report="60-Day DAM Disclosure Reports (the file 60d_DAM_ESR_Data: Energy Storage Resources)",
                            report_url=PAGE, document_list=LIST, tables=[TABLE])])
    ip.write_status("ercot_dam_esr", run_id, [{"table": TABLE, "status": "ok", "rows": rows,
                                               "detail": f"{len(held)} operating days {first} to {last}; {len(missing)} missing"}])
    line = f"{TABLE}.csv: rows={rows:,} days={len(held)} ({first}..{last}) missing={len(missing)}"
    print(line)
    log("  " + line)
    return 0


def last_day_held(path):
    """The last operating day (local, Central) the table holds: the one its header states ("Operating days held: N,
    first to last"), or, for a file whose header does not say, the newest hour among its last lines (the connector
    writes a day after a day). Raises ValueError for a file with no rows."""
    with open(path, encoding="utf-8", newline="") as f:
        for line in f:
            if not line.startswith("#"):
                break
            m = re.search(r"Operating days held: \d+, \d{4}-\d\d-\d\d to (\d{4}-\d\d-\d\d)", line)
            if m:
                return dt.date.fromisoformat(m.group(1))
    with open(path, "rb") as f:
        f.seek(0, os.SEEK_END)
        f.seek(max(0, f.tell() - 262_144))
        lines = f.read().decode("utf-8", "replace").splitlines()[1:]
    ts = [x.split(",")[2] for x in lines if x and not x.startswith("#") and x.count(",") >= len(COLS) - 1 and re.match(r"\d{4}-\d\d-\d\dT", x.split(",")[2])]
    if not ts:
        raise ValueError(f"{os.path.basename(path)} has no rows at its end")
    return pd.Timestamp(max(ts)).tz_convert(TZ).date()


def failed_days(path=None):
    """{operating day: reason} of the days that failed a check in a standing pull (a tracked file)."""
    path = path or MISSING_DAYS
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8", newline="") as f:
        return {dt.date.fromisoformat(r["operating_day"]): r["reason"] for r in csv.DictReader(f)}


def record_failed_day(day, reason, path=None):
    path = path or MISSING_DAYS
    new = not os.path.exists(path)
    with open(path, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        if new:
            w.writerow(["operating_day", "reason", "recorded_at"])
        w.writerow([day.isoformat(), " ".join(str(reason).split())[:300], dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")])


def next_day(docs, last, failed=()):
    """The standing pull's one day: (the first listed operating day after `last` that has not failed a check, its
    document, how many later days are listed and wait). (None, None, 0) when ERCOT lists nothing newer."""
    by_day = {}
    for d in sorted(docs, key=lambda d: d["PublishDate"]):
        by_day[operating_day(d)] = d  # a day posted twice: the later posting
    waiting = sorted(d for d in by_day if d > last and d not in failed)
    if not waiting:
        return None, None, 0
    return waiting[0], by_day[waiting[0]], len(waiting) - 1


def append_day(path, rows, day, run_id, log_name):
    """The table with one more day at its end: the header's counts moved on, every row already there copied as it is.

    Raises RuntimeError when the day is not after the table's last, or the rows would pass the row ceiling."""
    last = last_day_held(path)
    if day <= last:
        raise RuntimeError(f"{day} is not after the table's last day, {last}: nothing written")
    with open(path, encoding="utf-8", newline="") as f:
        head = []
        for line in f:
            if not line.startswith("#"):
                break
            head.append(line.rstrip("\r\n"))
    text = "\n".join(head)
    days = re.search(r"Operating days held: (\d+), (\d{4}-\d\d-\d\d) to (\d{4}-\d\d-\d\d)", text)
    holds = re.search(r"File holds ([\d,]+) rows", text)
    if not days or not holds:
        raise RuntimeError("the table's header does not state its days and rows: nothing written")
    n_old = int(holds.group(1).replace(",", ""))
    if n_old + len(rows) > MAX_ROWS:
        raise RuntimeError(f"{n_old + len(rows):,} rows would pass the ceiling of {MAX_ROWS:,}: nothing written")
    text = text.replace(days.group(0), f"Operating days held: {int(days.group(1)) + 1}, {days.group(2)} to {day.isoformat()}")
    text = text.replace(holds.group(0), f"File holds {n_old + len(rows):,} rows")
    text = re.sub(r"# Retrieved: \S+ \(UTC\)", f"# Retrieved: {run_id} (UTC)", text)
    text = re.sub(r"# Run log: \S+", f"# Run log: warehouse/output/logs/{log_name}", text)
    tmp = path + ".tmp"
    n = 0
    with open(path, encoding="utf-8", newline="") as old, open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(text + "\n")
        seen_cols = False
        for line in old:
            if line.startswith("#"):
                continue
            if not seen_cols:
                if line.rstrip("\r\n").split(",") != COLS:
                    raise RuntimeError("the table's columns are not the connector's: nothing written")
                seen_cols = True
                f.write(",".join(COLS) + "\n")
                continue
            f.write(line if line.endswith("\n") else line + "\n")
            n += 1
        rows[COLS].to_csv(f, index=False, header=False, lineterminator="\n")
    if n != n_old:
        os.remove(tmp)
        raise RuntimeError(f"the table holds {n:,} rows and its header says {n_old:,}: nothing written")
    os.replace(tmp, path)
    return n_old + len(rows)


def daily(log, run_id, get=None, run=None, table_path=None, missing_path=None, pause=PAUSE):
    """The standing pull: one zip, the next operating day, added to the table; then the tables built from it.

    Returns 0 when a day was added or ERCOT lists nothing newer, 1 when the day failed a check or a builder failed."""
    import subprocess
    get = get or requests.get
    run = run or subprocess.run
    path = table_path or os.path.join(ip.OUT_DIR, TABLE + ".csv")
    if ip.paused("ercot"):
        raise SystemExit(ip.pause_line("ercot"))
    if not os.path.exists(path):
        print(f"ercot_storage_dam SKIPPED: {TABLE} is not on this machine, so no zip was requested and nothing was built")
        return int(os.environ.get("ERW_SKIP_EXIT") or 0)
    if table_path is None:
        ip._require_lock(path, f"writing {TABLE}")
    last = last_day_held(path)
    r = get(LIST, headers=UA, timeout=120)
    r.raise_for_status()
    docs = [x["Document"] for x in json.loads(r.text)["ListDocsByRptTypeRes"]["DocumentList"]]
    day, doc, waiting = next_day(docs, last, failed_days(missing_path))
    if day is None:
        line = f"{TABLE}.csv: rows=unchanged; ERCOT lists no operating day after {last}: nothing requested"
        print(line, flush=True)
        log(line)
        return 0
    if waiting:
        line = (f"::notice::{waiting} more operating day{'s' if waiting != 1 else ''} after {day} are listed and not held: one zip a run, so the table is "
                f"{waiting} day{'s' if waiting != 1 else ''} further behind than ERCOT's 60 until a person approves more")
        print(line, flush=True)
        log(line)
    name, url, size = doc["ConstructedName"], FILE.format(doc=doc["DocID"]), int(doc["ContentSize"])
    held = held_zips()
    if name in held:
        with open(held[name], "rb") as f:
            content = f.read()
        when = ({m["file"]: m for m in manifest()}.get(name, {}).get("retrieved_at")
                or dt.datetime.fromtimestamp(os.path.getmtime(held[name]), dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
        log(f"{day}: {name} is on this machine; not requested")
    else:
        if size > DAILY_MAX_BYTES:
            raise RuntimeError(f"{day}: its zip is listed at {size:,} bytes, above the {DAILY_MAX_BYTES:,} a daily zip may be: not requested")
        time.sleep(pause)
        g = get(url, headers=UA, timeout=300)
        if g.status_code != 200 or len(g.content) != size:
            raise IOError(f"{day}: HTTP {g.status_code}, {len(g.content):,} bytes of {size:,}; nothing written (one request, not repeated)")
        content = g.content
        when = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        os.makedirs(ZIPS, exist_ok=True)
        with open(os.path.join(ZIPS, name) + ".tmp", "wb") as f:
            f.write(content)
        os.replace(os.path.join(ZIPS, name) + ".tmp", os.path.join(ZIPS, name))
        manifest_add({"operating_day": day.isoformat(), "file": name, "doc_id": doc["DocID"], "url": url, "bytes": len(content),
                      "sha256": hashlib.sha256(content).hexdigest(), "published": doc["PublishDate"], "retrieved_at": when, "how": "requested daily"})
        log(f"{day}: {name}, {len(content):,} bytes requested (the standing pull's one zip)")
    try:
        fname, df = read_esr(content)
        rows = to_rows(df, day, url, when, ip.utc_iso(pd.Timestamp(doc["PublishDate"])))
    except ValueError as e:
        record_failed_day(day, e, missing_path)
        line = f"{TABLE} FAILED: {day} failed a check and has no rows ({e}); recorded in warehouse/metadata/{os.path.basename(MISSING_DAYS)}, the next run goes on"
        print(line, flush=True)
        log(line)
        if table_path is None:
            ip.write_status("ercot_dam_esr", run_id, [{"table": TABLE, "status": "failed", "detail": f"{day}: {e}"[:300]}])
        return 1
    total = append_day(path, rows, day, run_id, os.path.basename(log.path) if hasattr(log, "path") else "")
    line = f"{TABLE}.csv: rows={total:,} added={len(rows):,} day={day} ({fname})"
    print(line, flush=True)
    log("  " + line)
    if table_path is None:
        ip.write_status("ercot_dam_esr", run_id, [{"table": TABLE, "status": "ok", "rows": total, "detail": f"the standing pull: {day} added, {len(rows):,} rows"}])
    rc = 0
    for cmd in ([sys.executable, MONTHLY_BUILDER], [sys.executable, OFFERS_BUILDER, "--days", day.isoformat()]):
        code = run(cmd, cwd=ROOT).returncode
        log(f"{os.path.basename(cmd[1])} {' '.join(cmd[2:])}: exit {code}")
        rc = rc or code
    return 1 if rc else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERCOT 60-Day DAM Disclosure: the Energy Storage Resources' day-ahead awards")
    ap.add_argument("--daily", action="store_true", help="the standing pull: one zip, the next operating day, added to the table; then the monthly tables")
    ap.add_argument("--pull", action="store_true", help="read each operating day's zip (asking ERCOT for one not held) and write the months")
    ap.add_argument("--write", action="store_true", help="write the table from the months (needs the data lock)")
    ap.add_argument("--from", dest="from_day", help="first operating day, YYYY-MM-DD (default: the first listed)")
    ap.add_argument("--to", dest="to_day", help="last operating day (default: the last listed)")
    ap.add_argument("--days", help="named operating days, comma separated: a probe, which writes no month")
    ap.add_argument("--offline", action="store_true", help="no request: the saved file list and the saved zips only")
    a = ap.parse_args(argv)
    if not (a.pull or a.write or a.daily):
        ap.error("--pull, --write or --daily")
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"ercot_dam_esr_{run_id}.log"))
    try:
        if a.daily:
            return daily(log, run_id)
        if a.pull:
            pull(a, log)
        if a.write:
            write(log, run_id)
    except Ceiling as e:
        line = f"STOPPED AT A CEILING: {e}"
        print(line, flush=True)
        log(line)
        return 3
    finally:
        log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
