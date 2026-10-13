#!/usr/bin/env python3
"""ERCOT's real-time reserve price adders, hourly, from 1 June 2014: the scarcity signal of the operating reserve
demand curve (ORDC), and the reliability deployment price adder beside it.

Energy Research Warehouse (ERW) connector, session 244 (docs/methods/ercot_rt_price_adders.md). Writes one series
table, warehouse/output/ercot_rtm_price_adders.csv:

    entity    ercot:system
    variable  <adder>_mean   the hour's time-weighted mean of the adder over ERCOT's SCED intervals
              <adder>_max    the largest value any SCED interval of the hour carried
              adders, by ERCOT's own names:
                rtorpa    Real-Time On-Line Reserve Price Adder (the ORDC adder),  1 June 2014 to 4 December 2025
                rtoffpa   Real-Time Off-Line Reserve Price Adder,                  1 June 2014 to 4 December 2025
                rtordpa   Real-Time On-Line Reliability Deployment Price Adder,    June 2015 to 4 December 2025
                rtrdpa    Real-Time Reliability Deployment Price Adder for energy, from 5 December 2025
    unit      USD/MWh
    freq      PT1H; ts_utc is the start of the hour, UTC
    market    ercot_rtm
    node      the adder, as ERCOT names its column (RTORPA, RTOFFPA, RTORDPA, RTRDPA)

    python warehouse/connectors/ercot_rt_adders.py                      # the documents not yet in the table
    python warehouse/connectors/ercot_rt_adders.py --full               # every document again (the first build)
    python warehouse/connectors/ercot_rt_adders.py --out-dir C:/scratch # a trial run: nothing in warehouse/output
    python warehouse/connectors/ercot_rt_adders.py --offline            # from the raw files only, no request

Source, on ERCOT's public reports site (the route ercot_as_prices.py uses): NP6-792-ER, report type 13231, one zip
per year, each one Excel workbook with a sheet per month and a row per SCED interval (about every five minutes).
Three forms, read by their own header rows:

  2014 and the first half of 2015   "Historical Real-Time Reserve ORDC Price Adder": RTORPA and RTOFFPA
  2015 to 4 December 2025           "Historical Real-Time ORDC and Reliability Deployment Price Adders and Reserves":
                                    the same two and RTORDPA (empty before June 2015)
  from 5 December 2025              "Historical Real-Time Price Adders by SCED Interval": RTRDPA. On that day ERCOT
                                    began clearing energy and ancillary services together in real time, and the
                                    ORDC adders ended: there is no RTORPA or RTOFFPA after it. The current year's
                                    file is republished every week

ERCOT posted two documents for 2015: the half-year one in the first form and the whole year in the second. The whole
year is read and the half-year one is not (the same intervals; check_overlap in the run log compares them).

From SCED intervals to hours. An interval's value holds from its stamp to the next interval's stamp. The hour's mean
weights each value by the seconds it held within the hour; the hour's max is the largest value that held in it.
Never fill: a value holds for at most MAX_GAP_MIN minutes, so an hour with a longer silence in it has seconds no
value covers, and an hour is written only when all of its 3,600 seconds are covered. The hours left out are logged
and reported as gaps. An empty cell is not a value and covers nothing. The first hour of the record and the last one
(still open) are left out by the same rule. Stamps are Central time with ERCOT's repeated-hour flag; they are read to
the second.

A document is parsed once: its address is in the rows it wrote (source_url), and a run without --full reads only the
documents whose address the table does not hold yet, with the last sheet of the document before, so the first hour
of a year has the interval that runs into it. The raw files stay in warehouse/raw/ercot_rt_adders/ and a file
already there is not requested again (iso_prices.fetch_raw). Each run: one request for the list, and one for each
document not held, 3 seconds apart.

Ceiling: 1,000,000 rows (session 244). A pull that would pass it writes nothing.

License: public. ERCOT's terms (https://www.ercot.com/help/terms, item 5): "raw data provided in public portions of
this website may be used, reproduced, and redistributed in compilations, charts, and analyses".
"""

import argparse
import datetime as dt
import io
import json
import os
import re
import sys
import traceback
import zipfile

import openpyxl
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "ercot_rtm_price_adders"
CONNECTOR = "ercot_rt_adders"
SOURCE = "ercot:NP6-792-ER"
REPORT = "Historical Real-Time ORDC and Reliability Deployment Price Adders and Reserves"
RTID = 13231
CEILING = 1_000_000
TZ = "America/Chicago"
MAX_GAP_MIN = 15        # a SCED interval's value holds until the next stamp, and for no longer than this
HOUR_S = 3600
ADDERS = ["RTORPA", "RTOFFPA", "RTORDPA", "RTRDPA"]
DOC_LIST = "https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId={}"
DOWNLOAD = "https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId={}"
PAGE = "https://www.ercot.com/mp/data-products/data-product-details?id=NP6-792-ER"
PAUSE = 3  # seconds between requests
STAMP, FLAG = "SCED Timestamp", "Repeated Hour Flag"
# the three names ERCOT has given the yearly documents, and the form each holds
FORMS = [(re.compile(r"^Historical Real-Time Reserve ORDC Price Adder_(\d{4})$"), "ordc"),
         (re.compile(r"^RTM_ORDC_REL_DPLY_PRC_ADDR_RSRV_(\d{4})$"), "ordc_rdpa"),
         (re.compile(r"^HIST_RT_SCED_PRC_ADDR_(\d{4})$"), "rdpa")]
FORM_ADDERS = {"ordc": ["RTORPA", "RTOFFPA"], "ordc_rdpa": ["RTORPA", "RTOFFPA", "RTORDPA"], "rdpa": ["RTRDPA"]}
MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]


def form_of(doc):
    """(form, year) of a listed document by its name, or None for a name this connector does not know."""
    for pat, form in FORMS:
        m = pat.match(doc["FriendlyName"].strip())
        if m:
            return form, int(m.group(1))
    return None


def month_of(sheet):
    """The month (1 to 12) a sheet's name stands for ("Jun_1", "Jan"), or None for a sheet that is not a month."""
    m = re.match(r"^([A-Za-z]{3})(?:_\d+)?$", sheet.strip())
    return MONTHS.index(m.group(1).lower()) + 1 if m and m.group(1).lower() in MONTHS else None


def read_sheet(ws, adders, what):
    """One month's sheet as rows (stamp, flag, each adder), the cells as the workbook stores them. The header row is
    the one that names the SCED stamp; a sheet with no interval under it is empty and returns no row."""
    ws.reset_dimensions()  # ERCOT's workbooks declare a one-cell sheet; read to the real end
    head, cols, rows = None, None, []
    for r in ws.iter_rows(values_only=True):
        if head is None:
            names = [str(c).strip() if c is not None else "" for c in r]
            if STAMP in names:
                head = names
                missing = [c for c in [STAMP, FLAG] + adders if c not in head]
                if missing or len(set(n for n in head if n)) != len([n for n in head if n]):
                    raise RuntimeError(f"{what}: header {head} lacks {missing} or repeats a name: layout changed")
                cols = [head.index(c) for c in [STAMP, FLAG] + adders]
            continue
        if r[cols[0]] is None:
            if any(c is not None for c in r):
                raise RuntimeError(f"{what}: a row without its SCED stamp: {list(r)[:8]}")
            continue
        rows.append([r[i] if i < len(r) else None for i in cols])
    if head is None:
        raise RuntimeError(f"{what}: no header row names the SCED stamp: layout changed")
    return rows


def parse_doc(raw, form, year, what, sheets=None):
    """A yearly zip as one frame: local (the naive Central stamp, to the second), flag, and a column per adder of the
    document's form (NaN for an empty cell). `sheets` limits it to those months (1 to 12)."""
    z = zipfile.ZipFile(io.BytesIO(raw))
    books = [n for n in z.namelist() if n.lower().endswith(".xlsx")]
    if len(books) != 1 or len(z.namelist()) != 1:
        raise RuntimeError(f"{what}: zip holds {z.namelist()}, expected one Excel workbook")
    wb = openpyxl.load_workbook(io.BytesIO(z.read(books[0])), read_only=True, data_only=True)
    adders = FORM_ADDERS[form]
    rows = []
    for ws in wb.worksheets:
        month = month_of(ws.title)
        if month is None:
            if ws.title.strip() != "Report Info":
                raise RuntimeError(f"{what}: a sheet named {ws.title!r} is neither a month nor the report's note")
            continue
        if sheets is not None and month not in sheets:
            continue
        got = read_sheet(ws, adders, f"{what}, sheet {ws.title}")
        for r in got:
            if not isinstance(r[0], dt.datetime):
                raise RuntimeError(f"{what}, sheet {ws.title}: a SCED stamp that is not a date and time: {r[0]!r}")
            if (r[0].year, r[0].month) != (year, month) and not (r[0] + dt.timedelta(seconds=1)).month == month:
                raise RuntimeError(f"{what}, sheet {ws.title}: a stamp of another month: {r[0]}")
        rows += got
    wb.close()
    x = pd.DataFrame(rows, columns=["local", "flag"] + adders)
    if x.empty:
        return x
    x["local"] = pd.to_datetime(x["local"]).dt.round("s")
    x["flag"] = x["flag"].astype(str).str.strip().str.upper()
    if not x["flag"].isin(["Y", "N"]).all():
        raise RuntimeError(f"{what}: repeated-hour flag not Y or N: {sorted(set(x['flag']) - {'Y', 'N'})[:5]}")
    for a in adders:
        bad = x[a].map(lambda v: v is not None and (isinstance(v, bool) or not isinstance(v, (int, float))))
        if bad.any():
            raise RuntimeError(f"{what}: {a} holds a cell that is not a number: {x.loc[bad, a].iloc[0]!r}")
        x[a] = pd.to_numeric(x[a], errors="raise")
    return x


def to_utc(local, flag):
    """ERCOT's Central stamps as UTC. The flag is Y for the second pass through the repeated hour of the autumn clock
    change; ambiguous=True means daylight time, the first pass, which ERCOT does not flag."""
    return local.dt.tz_localize(TZ, ambiguous=(flag == "N").values, nonexistent="raise").dt.tz_convert("UTC")


def hourly(ts, values, max_gap_min=MAX_GAP_MIN):
    """Hours from SCED intervals. `ts` are the UTC stamps in order, `values` one adder's value at each (NaN: no value).
    Returns a frame indexed by the hour's start with mean (time-weighted), max and covered (seconds, of 3,600).
    A value holds from its stamp to the next stamp, for at most max_gap_min minutes; a value that is NaN holds
    nothing. A stretch of at most that long touches two hours at the most, so each is split once."""
    t = pd.Series(pd.DatetimeIndex(ts)).reset_index(drop=True)
    v = pd.Series(values).reset_index(drop=True).astype(float)
    if not t.is_monotonic_increasing or t.duplicated().any():
        raise RuntimeError("SCED stamps are not in order or repeat")
    end = pd.concat([t.shift(-1), t + pd.Timedelta(minutes=max_gap_min)], axis=1).min(axis=1)  # the last stamp: no next, holds nothing
    end = end.where(t.shift(-1).notna(), t)
    keep = v.notna() & (end > t)
    t, v, end = t[keep], v[keep], end[keep]
    h0 = t.dt.floor("h")
    cut = h0 + pd.Timedelta(hours=1)
    first = pd.DataFrame({"hour": h0, "s": (end.where(end < cut, cut) - t).dt.total_seconds(), "v": v})
    over = end > cut
    second = pd.DataFrame({"hour": cut[over], "s": (end[over] - cut[over]).dt.total_seconds(), "v": v[over]})
    parts = pd.concat([first, second], ignore_index=True)
    parts["vs"] = parts["v"] * parts["s"]
    g = parts.groupby("hour").agg(covered=("s", "sum"), vs=("vs", "sum"), max=("v", "max"))
    g["mean"] = g["vs"] / g["covered"]
    return g[["mean", "max", "covered"]]


def doc_list(log, offline):
    raw, _ = ip.fetch_raw(CONNECTOR, DOC_LIST.format(RTID), log, offline=offline, fresh=True, pause=PAUSE)
    return [d["Document"] for d in json.loads(raw)["ListDocsByRptTypeRes"]["DocumentList"]]


def chosen(docs):
    """The documents to read, oldest first, as (document, form, year): every listed one whose name is known, but for
    the half-year document of a year that also has its whole-year one. A name not known is an error: a new form."""
    known = []
    for d in docs:
        f = form_of(d)
        if f is None:
            raise RuntimeError(f"NP6-792-ER lists a document this connector does not know: {d['FriendlyName']!r}")
        known.append((d, f[0], f[1]))
    whole = {y for _, form, y in known if form == "ordc_rdpa"}
    out = [k for k in known if not (k[1] == "ordc" and k[2] in whole)]
    order = {"ordc": 0, "ordc_rdpa": 1, "rdpa": 2}
    out.sort(key=lambda k: (k[2], order[k[1]]))
    newest = {}
    for d, form, y in out:  # one document a (year, form): the one published last
        if (y, form) not in newest or d["PublishDate"] > newest[(y, form)][0]["PublishDate"]:
            newest[(y, form)] = (d, form, y)
    return [newest[k] for k in sorted(newest, key=lambda k: (k[0], order[k[1]]))]


def held_urls(out_dir=None):
    """The document addresses the table already holds rows from (its source_url column)."""
    path = os.path.join(out_dir or ip.OUT_DIR, NAME + ".csv")
    if not os.path.exists(path):
        return set()
    skip = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            skip += 1
    return set(pd.read_csv(path, skiprows=skip, usecols=["source_url"], dtype=str)["source_url"].unique())


def pull(log, offline=False, full=False):
    """(rows, gaps, summary). rows: long (adder, hour, mean, max, source_url, retrieved_at, vintage)."""
    docs = chosen(doc_list(log, offline))
    years = sorted({y for _, _, y in docs})
    missing = [y for y in range(years[0], years[-1] + 1) if y not in years]
    if years[0] != 2014 or missing:
        raise RuntimeError(f"NP6-792-ER: the list begins in {years[0]} and lacks {missing}: expected every year from 2014")
    held = set() if full else held_urls()
    todo = [i for i, (d, _, _) in enumerate(docs) if DOWNLOAD.format(d["DocID"]) not in held]
    if not todo:
        log("  every listed document is in the table already: nothing to read")
        return pd.DataFrame(), [], "no new document"
    log(f"  {len(docs)} documents listed; {len(todo)} to read: {[docs[i][0]['FriendlyName'] for i in todo]}")
    frames = []
    for i, (d, form, year) in enumerate(docs):
        lead = i not in todo and (i + 1) in todo  # the document before one that is read: its last sheet, for the first hour
        if i not in todo and not lead:
            continue
        url = DOWNLOAD.format(d["DocID"])
        raw, rec = ip.fetch_raw(CONNECTOR, url, log, offline=offline, pause=PAUSE)
        if raw[:2] != b"PK":
            raise RuntimeError(f"{d['FriendlyName']}: the download is not a zip ({raw[:40]!r})")
        x = parse_doc(raw, form, year, d["FriendlyName"], sheets=[12] if lead else None)
        if x.empty:
            log(f"  {d['FriendlyName']}: no interval")
            continue
        x["ts"] = to_utc(x["local"], x["flag"])
        x["form"], x["lead"] = form, lead
        x["source_url"], x["retrieved_at"] = url, rec["retrieved_at"]
        x["vintage"] = ip.utc_iso(pd.Timestamp(d["PublishDate"]))
        log(f"  {d['FriendlyName']} ({form}{', its last sheet only' if lead else ''}), published {d['PublishDate']}: "
            f"{len(x)} SCED intervals, {x['ts'].min()} to {x['ts'].max()}")
        frames.append(x)
    sced = pd.concat(frames, ignore_index=True).sort_values("ts").reset_index(drop=True)
    if sced["ts"].duplicated().any():
        raise RuntimeError(f"{int(sced['ts'].duplicated().sum())} SCED stamps repeat across documents")
    step = sced["ts"].diff().dt.total_seconds().dropna() / 60
    log(f"  {len(sced)} SCED intervals in all; minutes between stamps: median {step.median():.2f}, 99th percentile "
        f"{step.quantile(0.99):.2f}, longest {step.max():.1f}; longer than {MAX_GAP_MIN} minutes: {int((step > MAX_GAP_MIN).sum())}")
    out, gaps = [], []
    for a in ADDERS:
        if a not in sced.columns or sced[a].notna().sum() == 0:
            continue
        # every stamp bounds the value before it, whichever form its document has: the last ORDC value of 4 December
        # 2025 holds to the first stamp of the next form. Within the adder's own span every hour is written or a gap
        h = hourly(sced["ts"], sced[a])
        h = h.reindex(pd.date_range(h.index.min(), h.index.max(), freq="h"))
        h["covered"] = h["covered"].fillna(0)
        full_hours = h[h["covered"].round(3) == HOUR_S]
        short = h[h["covered"].round(3) != HOUR_S]
        # an hour holds the document of its first interval; the hours of a document read only for its last sheet are not rewritten
        src = sced.assign(hour=sced["ts"].dt.floor("h")).drop_duplicates("hour").set_index("hour")
        f = full_hours.join(src[["source_url", "retrieved_at", "vintage", "lead"]], how="left")
        if f["source_url"].isna().any():
            raise RuntimeError(f"{a}: {int(f['source_url'].isna().sum())} complete hours begin with no interval of their own")
        f = f[~f["lead"].astype(bool)]
        edge = {h.index.min(), h.index.max()}
        inner = [t for t in short.index if t not in edge and not bool(src["lead"].get(t, False))]
        for t in inner:
            gaps.append(f"{a} {ip.utc_iso(t)}: {short.loc[t, 'covered']:.0f} of {HOUR_S} seconds covered")
        log(f"  {a}: {len(f)} hours written, {ip.utc_iso(f.index.min())} to {ip.utc_iso(f.index.max())}; "
            f"{len(inner)} hours left out for a silence longer than {MAX_GAP_MIN} minutes; the first and the last hour of its span are open")
        out.append(pd.DataFrame({"adder": a, "hour": f.index, "mean": f["mean"].values, "max": f["max"].values,
                                 "source_url": f["source_url"].values, "retrieved_at": f["retrieved_at"].values,
                                 "vintage": f["vintage"].values}))
    for g in gaps[:200]:
        log(f"  gap, left out: {g}")
    rows = pd.concat(out, ignore_index=True)
    return rows, gaps, f"{len(todo)} documents read"


def to_series(rows):
    parts = []
    for stat in ("mean", "max"):
        parts.append(pd.DataFrame({
            "entity": "ercot:system", "variable": rows["adder"].str.lower() + "_" + stat, "ts_utc": rows["hour"].map(ip.utc_iso),
            "value": rows[stat].round(4), "unit": "USD/MWh", "freq": "PT1H", "geo": "US-TX", "market": "ercot_rtm",
            "node": rows["adder"], "source": SOURCE, "source_url": rows["source_url"], "retrieved_at": rows["retrieved_at"],
            "vintage": rows["vintage"],
        }))
    s = pd.concat(parts, ignore_index=True)
    return s.sort_values(["variable", "ts_utc"]).reset_index(drop=True)[ip.SERIES_COLS]


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: ERCOT's real-time reserve price adders, hourly")
    ap.add_argument("--out-dir", help="write the table, log, registry and status under this directory instead of "
                    "the repository (raw files stay in warehouse/raw)")
    ap.add_argument("--offline", action="store_true", help="read the raw files only; make no request")
    ap.add_argument("--full", action="store_true", help="read every listed document again, not only those the table lacks")
    a = ap.parse_args(argv)
    if ip.paused("ercot"):  # session 89: a paused publisher is never requested
        print(f"{CONNECTOR}: ERCOT is paused (warehouse/metadata/paused_sources.csv); nothing requested")
        return 0
    raw_dir = ip.RAW_DIR
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
        ip.RAW_DIR = raw_dir  # source documents are kept once, in warehouse/raw, whatever the output directory
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        rows, gaps, what = pull(log, a.offline, a.full)
        if rows.empty:
            print(f"{NAME}: {what}; the table is as it was")
            results.append(dict(table=NAME, market="RTM", status="ok", detail=what))
        else:
            s = to_series(rows)
            if len(s) > CEILING:
                raise RuntimeError(f"{len(s)} rows would pass the ceiling of {CEILING}; nothing written")
            header = [
                "Energy Research Warehouse (ERW): ERCOT's real-time reserve price adders, hourly: the operating reserve "
                "demand curve's adders and the reliability deployment price adder",
                "Shape: series (docs/datastandard.md v0). Unit USD/MWh. ts_utc is the start of the hour, UTC (ERCOT "
                "publishes a row per SCED interval, stamped in Central time).",
                "Variables: <adder>_mean is the hour's time-weighted mean over the SCED intervals, <adder>_max the "
                "largest value an interval of the hour carried. rtorpa: on-line reserve price adder; rtoffpa: off-line "
                "reserve price adder (both 1 June 2014 to 4 December 2025, when the ORDC adders ended); rtordpa: on-line "
                "reliability deployment price adder (June 2015 to 4 December 2025); rtrdpa: reliability deployment "
                "price adder for energy (from 5 December 2025).",
                f"Never filled: a SCED interval's value holds to the next stamp, for at most {MAX_GAP_MIN} minutes; an "
                f"hour is written only when all 3,600 of its seconds are covered. {len(gaps)} hours are left out of "
                "this run for a longer silence" + (": " + "; ".join(gaps[:12]) + ("; and more, in the run log" if len(gaps) > 12 else "") if gaps else "") + ".",
                f"Retrieved: {run_id} (UTC) by warehouse/connectors/ercot_rt_adders.py",
                f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
                f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git; each run's manifest.csv lists each file and URL)",
                f"Source: {SOURCE} ERCOT, {REPORT}, {PAGE}",
                "License: public. ERCOT terms of use, item 5: raw data in public portions of the website may be used, "
                "reproduced, and redistributed in compilations, charts, and analyses.",
                "Method: docs/methods/ercot_rt_price_adders.md",
            ]
            ip.write_csv(s, NAME, header, log)
            ip.update_sources([dict(source=SOURCE, publisher=ip.ISO_PUBLISHERS["ercot"], report=REPORT, report_url=PAGE,
                                    document_list=DOC_LIST.format(RTID), tables=[NAME])])
            results.append(dict(table=NAME, market="RTM", status="ok", detail=f"{len(s)} rows of {CEILING}; {what}"))
            for g in gaps[:50]:
                results.append(dict(table=NAME, market="RTM", status="gap", detail=g))
    except Exception:
        tb = ip.redact(traceback.format_exc())
        last = tb.strip().splitlines()[-1]
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{CONNECTOR} {NAME} FAILED, no output file written: {last}", file=sys.stderr)
        results.append(dict(table=NAME, market="RTM", status="failed", detail=last[:300]))
    ip.write_status(CONNECTOR, run_id, results)
    failures = sum(r["status"] == "failed" for r in results)
    log(f"done, failures={failures}")
    log.close()
    print(f"{CONNECTOR} run log: {os.path.relpath(log.path, ip.ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
