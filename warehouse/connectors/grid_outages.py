#!/usr/bin/env python3
"""Generation out of service as the operators publish it: SPP by balancing area and fuel, CAISO by planned and forced,
hourly.

Energy Research Warehouse (ERW) connector, chain 601 part D (session 9000; docs/methods/grid_outages.md). Writes one
series table, generation_outages_hourly (the chain named it generation_outages; the data standard asks three parts):

    entity    spp:<BAA as the file names it>   spp:SPP, spp:SWPW and spp:Total, each as SPP prints it
              caiso:ISO                        the California ISO's balancing area, as its report covers it
    variable  SPP:   outage_mw_total ("Outaged MW"), outage_mw_coal, outage_mw_oil ("Diesel Fuel Oil MW"),
                     outage_mw_hydro, outage_mw_gas ("Natural Gas MW"), outage_mw_nuclear, outage_mw_solar,
                     outage_mw_waste_disposal, outage_mw_wind, outage_mw_waste_heat, outage_mw_other
              CAISO: outage_mw_planned, outage_mw_forced, outage_mw_total: the megawatts curtailed in each hour,
                     the report's curtailment rows weighted by the part of the hour each covers
    unit MW, freq PT1H, ts_utc the start of the hour

    python warehouse/connectors/grid_outages.py --operator spp --start 2025-01-01
    python warehouse/connectors/grid_outages.py --operator caiso --start 2026-01-01
    python warehouse/connectors/grid_outages.py --out-dir C:/scratch ...       # a trial

Sources
    SPP: the Marketplace portal's file browser, folder capacity-of-generation-on-outage ("Capacity of Generation on
    Outage"), one csv a day, Capacity-Gen-Outage-<YYYYMMDD>.csv, each holding the day it is published and the six
    after it. Only the hours of the publishing day are kept: each hour is the outage SPP published that morning for
    it, never a forecast for a later day. Archived years are one zip (/<year>/<year>.zip); the folder says which.
    CAISO: "Curtailed and Non-Operational Generator Prior Trade Date Report", one workbook a trade date, at
    https://www.caiso.com/documents/curtailed-non-operational-generator-prior-trade-date-report-<date>.xlsx (the date's
    form changed on 2024-05-31 and 2025-01-13; 2024-06-01 has an "and" in the name), from 2021-06-17. Sheet
    PREV_DAY_OUTAGES: each row an outage's curtailment interval, its type (PLANNED or FORCED), nature of work, start,
    end (empty while it goes on) and megawatts curtailed. An hour's figure is the sum over rows of the megawatts times
    the share of the hour the row's interval covers, clipped to the trade date; an empty end runs to the trade date's end.

Never fill. A day whose document is missing is a gap, logged and named in the header. A (entity, variable, day) is
written only when every hour of the operating day is there.

Licenses: public, with citation. SPP's terms: "Permission is implicitly granted to copy and distribute ... (with
appropriate citation) EXCEPT when such materials will be used ... within a commercial publication". CAISO: "freely
available for public use consistent with the general policies of the Public Records Act" (credit the California ISO).
ERCOT's outage reports are only on paths its robots file disallows (the owner's ruling 2 of 6 November 2026); PJM,
NYISO and ISO-NE are held by license and MISO is paused: none is asked.
"""

import argparse
import datetime as dt
import io
import os
import sys
import time
import traceback
import zipfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402
import grid_congestion as gc  # noqa: E402

CONNECTOR = "grid_outages"
TABLE = "generation_outages_hourly"
SPP_FS = "capacity-of-generation-on-outage"
SPP_PAGE = "https://portal.spp.org/pages/capacity-of-generation-on-outage"
SPP_SOURCE = "spp:CAP-GEN-OUTAGE"
SPP_REPORT = "Capacity of Generation on Outage"
SPP_FIRST = "2016-01-01"
SPP_FUELS = {"Outaged MW": "outage_mw_total", "Coal MW": "outage_mw_coal", "Diesel Fuel Oil MW": "outage_mw_oil",
             "Hydro MW": "outage_mw_hydro", "Natural Gas MW": "outage_mw_gas", "Nuclear MW": "outage_mw_nuclear",
             "Solar MW": "outage_mw_solar", "Waste Disposal MW": "outage_mw_waste_disposal", "Wind MW": "outage_mw_wind",
             "Waste Heat MW": "outage_mw_waste_heat", "Other MW": "outage_mw_other"}
CAISO_PAGE = "https://www.caiso.com/library/curtailed-and-non-operational-generators"
CAISO_SOURCE = "caiso:CURTAILED-NONOP-GEN"
CAISO_REPORT = "Curtailed and Non-Operational Generator Prior Trade Date Report"
CAISO_FIRST = "2021-06-17"
CAISO_DOC = "https://www.caiso.com/documents/curtailed-non-operational-generator-prior-trade-date-report-{}.xlsx"
CAISO_DOC_AND = "https://www.caiso.com/documents/curtailed-and-non-operational-generator-prior-trade-date-report-{}.xlsx"


def caiso_url(day):
    d = pd.Timestamp(day)
    if d == pd.Timestamp("2024-05-31"):
        s = d.strftime("%Y-%m-%d")
    elif d < pd.Timestamp("2024-05-31") or d > pd.Timestamp("2025-01-12"):
        s = d.strftime("%Y%m%d")
    else:
        s = d.strftime("%b-%d-%Y").lower()
    return (CAISO_DOC_AND if d == pd.Timestamp("2024-06-01") else CAISO_DOC).format(s)


# ---------------------------------------------------------------------------
# SPP
# ---------------------------------------------------------------------------

def spp_docs(days, log, offline):
    docs = []
    for year in sorted({d.year for d in days}, reverse=True):
        ydays = [d for d in days if d.year == year]
        if gc.spp_archived(SPP_FS, year, log, offline):
            docs.append(dict(url=gc.SPP_FILE.format(fs=SPP_FS, path=f"{year}/{year}.zip"), year=year, days=ydays, fresh=False))
        else:
            for d in sorted(ydays, reverse=True):
                docs.append(dict(url=gc.SPP_FILE.format(fs=SPP_FS, path=d.strftime("%Y/%m/Capacity-Gen-Outage-%Y%m%d.csv")),
                                 days=[d], fresh=gc.stale(d)))
    return docs


def spp_texts(raw, doc, gaps):
    if "year" not in doc:
        return [(doc["days"][0], raw.decode("utf-8-sig"))]
    z = zipfile.ZipFile(io.BytesIO(raw))
    names = {}
    for n in z.namelist():
        base = n.rsplit("/", 1)[-1]
        if base.startswith("Capacity-Gen-Outage-") and base.endswith(".csv"):
            names[base[len("Capacity-Gen-Outage-"):len("Capacity-Gen-Outage-") + 8]] = n
    out = []
    for d in doc["days"]:
        n = names.get(d.strftime("%Y%m%d"))
        if n is None:
            gaps.append(f"SPP {SPP_REPORT} {d.date()}: not in the {doc['year']} zip")
            continue
        out.append((d, z.read(n).decode("utf-8-sig")))
    return out


def spp_rows(day, text, rec):
    x = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)
    x.columns = [c.strip() for c in x.columns]
    for c in x.columns:
        x[c] = x[c].str.strip()
    hour_col = "Market Hour" if "Market Hour" in x.columns else None
    baa = "BAA" if "BAA" in x.columns else None
    if hour_col is None or baa is None or "Outaged MW" not in x.columns:
        raise RuntimeError(f"SPP outage file {day.date()}: columns {list(x.columns)}: layout changed")
    x["ts"] = gc.spp_time(x[hour_col]) - pd.Timedelta(hours=1)
    hours = set(gc.day_hours(day, gc.SPP_TZ)) | set(gc.day_hours(pd.Timestamp(day) + pd.Timedelta(days=1), gc.SPP_TZ))
    x = x[x["ts"].isin(hours)]  # the publishing day and the next; pull() keeps for each hour the newest file of its day or the day before
    out = []
    for col, var in SPP_FUELS.items():
        if col not in x.columns:
            continue
        s = x[x[col] != ""]
        out.append(pd.DataFrame({"place": s[baa], "variable": var, "ts": s["ts"],
                                 "value": pd.to_numeric(s[col], errors="raise")}))
    rows = pd.concat(out, ignore_index=True)
    return rows.assign(day=day, ns="spp", geo=gc.SPP_GEO, source=SPP_SOURCE, source_url=rec["url"],
                       retrieved_at=rec["retrieved_at"])


# ---------------------------------------------------------------------------
# CAISO
# ---------------------------------------------------------------------------

def caiso_frame(raw, day):
    b = io.BytesIO(raw)
    t = pd.read_excel(b, usecols="B:M", sheet_name="PREV_DAY_OUTAGES", engine="openpyxl", header=None)
    first = t[t.columns[0]].astype(str).str.strip()
    hit = first[first == "OUTAGE MRID"]
    if hit.empty:
        raise RuntimeError(f"CAISO outage report {day.date()}: no OUTAGE MRID header in sheet PREV_DAY_OUTAGES")
    b.seek(0)
    x = pd.read_excel(b, usecols="B:M", skiprows=int(hit.index[0]), sheet_name="PREV_DAY_OUTAGES", engine="openpyxl")
    x = x.dropna(axis=1, how="all")
    x.columns = [str(c).strip() for c in x.columns]
    need = ["OUTAGE MRID", "OUTAGE TYPE", "CURTAILMENT START DATE TIME", "CURTAILMENT END DATE TIME", "CURTAILMENT MW"]
    if any(c not in x.columns for c in need):
        raise RuntimeError(f"CAISO outage report {day.date()}: columns {list(x.columns)}: layout changed")
    return x


def caiso_rows(day, raw, rec):
    x = caiso_frame(raw, day)
    x = x[x["OUTAGE MRID"].notna()]
    tz = gc.CAISO_TZ
    a = pd.Timestamp(day).tz_localize(tz)
    b = (pd.Timestamp(day) + pd.Timedelta(days=1)).tz_localize(tz)
    st = pd.to_datetime(x["CURTAILMENT START DATE TIME"]).dt.tz_localize(tz, ambiguous=True, nonexistent="shift_forward")
    en = pd.to_datetime(x["CURTAILMENT END DATE TIME"]).dt.tz_localize(tz, ambiguous=True, nonexistent="shift_forward")
    en = en.fillna(b)
    mw = pd.to_numeric(x["CURTAILMENT MW"], errors="coerce").fillna(0.0)
    kind = x["OUTAGE TYPE"].astype(str).str.strip().str.upper()
    res = x["RESOURCE ID"].astype(str).str.strip() if "RESOURCE ID" in x.columns else x["OUTAGE MRID"].astype(str)
    pmax = pd.to_numeric(x["RESOURCE PMAX MW"], errors="coerce") if "RESOURCE PMAX MW" in x.columns else pd.Series(float("nan"), index=x.index)
    # the same curtailment printed twice (outage, start, end, megawatts all equal) counts once
    once = ~pd.DataFrame({"m": x["OUTAGE MRID"].astype(str), "s": st, "e": en, "w": mw}).duplicated()
    hours = gc.day_hours(day, tz)
    out = []
    for h in hours:
        h0 = h.tz_convert(tz)
        h1 = h0 + pd.Timedelta(hours=1)
        lo = st.where(st > h0, h0)
        hi = en.where(en < h1, h1)
        share = ((hi - lo).dt.total_seconds() / 3600.0).clip(lower=0)
        w = mw * share * once
        # overlapping outages of one resource: its hour is capped at its Pmax, shared among its rows in proportion
        tot = w.groupby(res).transform("sum")
        cap = pmax.groupby(res).transform("max")
        factor = (cap / tot).where((tot > cap) & (cap > 0), 1.0).fillna(1.0)
        w = w * factor
        planned = float(w[kind == "PLANNED"].sum())
        forced = float(w[kind == "FORCED"].sum())
        out += [("outage_mw_planned", h, planned), ("outage_mw_forced", h, forced), ("outage_mw_total", h, float(w.sum()))]
    other = sorted(set(kind) - {"PLANNED", "FORCED"})
    rows = pd.DataFrame(out, columns=["variable", "ts", "value"])
    rows["value"] = rows["value"].round(3)
    return rows.assign(place="ISO", day=pd.Timestamp(day), ns="caiso", geo=gc.CAISO_GEO, source=CAISO_SOURCE,
                       source_url=rec["url"], retrieved_at=rec["retrieved_at"]), other


# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------

def complete(rows, tz, gaps):
    keep = []
    for (day, place, var), g in rows.groupby(["day", "place", "variable"], sort=True):
        hours = set(gc.day_hours(day, tz))
        if len(g) == len(hours) and set(g["ts"]) == hours:
            keep.append(g)
        else:
            gaps.append(f"{place} {var} {pd.Timestamp(day).date()}: {len(g)} of {len(hours)} hours, left out")
    return pd.concat(keep, ignore_index=True) if keep else rows.iloc[0:0]


def series(rows):
    return pd.DataFrame({
        "entity": rows["ns"] + ":" + rows["place"], "variable": rows["variable"], "ts_utc": rows["ts"].map(gc.utc_text),
        "value": rows["value"], "unit": "MW", "freq": "PT1H", "geo": rows["geo"], "market": "", "node": "",
        "source": rows["source"], "source_url": rows["source_url"], "retrieved_at": rows["retrieved_at"], "vintage": "",
    })[ip.SERIES_COLS]


def pull(op, start, until, log, offline, gaps, notes):
    first = SPP_FIRST if op == "spp" else CAISO_FIRST
    a = max(pd.Timestamp(start), pd.Timestamp(first))
    days = list(pd.date_range(a, pd.Timestamp(until) - pd.Timedelta(days=1), freq="D"))
    if op == "spp":  # the day before the first: its file holds the first day's hours 0 to 2
        days = [a - pd.Timedelta(days=1)] + days
    frames, t0 = [], time.time()
    if op == "spp":
        docs = spp_docs(days, log, offline)
        for i, doc in enumerate(docs):
            try:
                raw, rec = ip.fetch_raw(CONNECTOR, doc["url"], log, offline=offline, fresh=doc["fresh"])
            except ip.SourceGap as exc:
                gaps.append(f"SPP {SPP_REPORT} {doc['days'][0].date()}: not at the source")
                log(f"  gap: {exc}")
                continue
            for day, text in spp_texts(raw, doc, gaps):
                frames.append(spp_rows(day, text, rec))
            if not rec.get("cached"):
                time.sleep(1)
            if i % 25 == 0:
                print(f"{CONNECTOR} spp: {i + 1} of {len(docs)} documents, {time.time() - t0:.0f} s", flush=True)
        tz = gc.SPP_TZ
    else:
        for i, day in enumerate(sorted(days, reverse=True)):
            url = caiso_url(day)
            try:
                raw, rec = ip.fetch_raw(CONNECTOR, url, log, offline=offline, fresh=gc.stale(day))
            except (ip.SourceGap, RuntimeError) as exc:
                gaps.append(f"CAISO {CAISO_REPORT} {day.date()}: not at the source ({str(exc)[:80]})")
                log(f"  gap: {exc}")
                continue
            try:
                rows, other = caiso_rows(day, raw, rec)
            except Exception as exc:  # a workbook that does not read is a gap, named
                gaps.append(f"CAISO {CAISO_REPORT} {day.date()}: did not read ({str(exc)[:80]})")
                log(f"  gap: {day.date()} {exc!r}")
                continue
            if other:
                notes.add(f"CAISO outage types other than PLANNED and FORCED (in the total only): {', '.join(other)}")
            frames.append(rows)
            if not rec.get("cached"):
                time.sleep(1)
            if i % 25 == 0:
                print(f"{CONNECTOR} caiso: {i + 1} of {len(days)} days, {time.time() - t0:.0f} s", flush=True)
        tz = gc.CAISO_TZ
    if not frames:
        return None
    rows = pd.concat(frames, ignore_index=True)
    if op == "spp":
        # each hour from the newest file published on its own local day or the day before (SPP's file starts at the
        # publishing morning's 03:00 Central, so hours 0 to 2 come from the day before's file)
        rows["pub"] = rows["day"]
        rows["day"] = rows["ts"].dt.tz_convert(tz).dt.tz_localize(None).dt.normalize()
        rows = rows[(rows["pub"] == rows["day"]) | (rows["pub"] == rows["day"] - pd.Timedelta(days=1))]
        rows = rows.sort_values("pub").drop_duplicates(["place", "variable", "ts"], keep="last")
        rows = rows[(rows["day"] >= a) & (rows["day"] < pd.Timestamp(until))].drop(columns=["pub"])
    rows = complete(rows, tz, gaps)
    return series(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: generation out of service (SPP, CAISO)")
    ap.add_argument("--operator", choices=["spp", "caiso", "all"], default="all")
    ap.add_argument("--start", default="2026-01-01")
    ap.add_argument("--until")
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
    ops = ["spp", "caiso"] if a.operator == "all" else [a.operator]
    results, frames, gaps, notes, sources, regs = [], [], [], set(), [], []
    try:
        for op in ops:
            if ip.paused(op):
                log(f"{op}: {ip.pause_line(op)}")
                continue
            s = pull(op, a.start, until, log, a.offline, gaps, notes)
            src, rep, page = (SPP_SOURCE, SPP_REPORT, SPP_PAGE) if op == "spp" else (CAISO_SOURCE, CAISO_REPORT, CAISO_PAGE)
            sources.append(f"{src} {ip.ISO_PUBLISHERS[op]}, {rep}, {page}")
            regs.append(dict(source=src, publisher=ip.ISO_PUBLISHERS[op], report=rep, report_url=page, document_list=page,
                             license="public", tables=[TABLE]))
            if s is not None and len(s):
                frames.append(s)
        if not frames:
            raise RuntimeError("no row was read; nothing written")
        new = pd.concat(frames, ignore_index=True)
        if new.duplicated(gc.KEY).any():
            raise RuntimeError("rows repeat a key")
        hdr = [
            "Energy Research Warehouse (ERW): generation out of service, hourly, as SPP and CAISO publish it",
            "Shape: series (docs/datastandard.md v0). MW. ts_utc is the start of the hour, UTC.",
            "SPP: megawatts on outage by balancing area (SPP, SWPW, Total as SPP prints them) and fuel, the hours of each "
            "publishing day only. CAISO: megawatts curtailed, planned and forced and their total, from the prior trade "
            "date report's curtailment rows weighted by the part of each hour they cover.",
            gc.NOT_ASKED.replace("Not asked:", "Not asked for outages:"),
            *sorted(notes),
            f"Gaps in this run: {len(gaps)}" + (": " + "; ".join(gaps[:25]) if gaps else "") + ".",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/{CONNECTOR}.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git; each run's manifest.csv lists each file and URL)",
            "Source: " + "; ".join(sources),
            gc.LICENSE_LINE,
            "Method: docs/methods/grid_outages.md",
        ]
        gc.write(TABLE, new.assign(market=new["market"].fillna("")), ip.SERIES_COLS, hdr, log)
        ip.update_sources(regs)
        results.append(dict(table=TABLE, market="", status="ok", detail=f"{len(new)} rows"))
        results += [dict(table=TABLE, market="", status="gap", detail=g[:300]) for g in gaps]
    except Exception:
        tb = ip.redact(traceback.format_exc())
        last = tb.strip().splitlines()[-1]
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{CONNECTOR} {TABLE} FAILED, no output file written: {last}", file=sys.stderr)
        results.append(dict(table=TABLE, market="", status="failed", detail=last[:300]))
    ip.write_status(CONNECTOR, run_id, results)
    failures = sum(r["status"] == "failed" for r in results)
    log(f"done, failures={failures}")
    log.close()
    print(f"{CONNECTOR} run log: {os.path.relpath(log.path, ip.ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
