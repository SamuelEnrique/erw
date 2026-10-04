"""ERCOT's 60-day disclosure data: a sample, for scoping what real batteries earned (session 108).

    python warehouse/analysis/ercot_disclosure_sample.py --month 2026-07          # ask ERCOT for the month's files
    python warehouse/analysis/ercot_disclosure_sample.py --month 2026-07 --from-dir DIR   # read zips saved by an earlier run

An approved sample pull: the storage resources' day-ahead awards for one month, ceiling 300,000 rows, USD 0. It is
analysis, not a warehouse table: it writes under warehouse/output/analysis_internal/ (not in coverage, the archive,
Redivis or Supabase) and saves the zips it downloads under warehouse/raw/ercot_60d_dam/<run>/.

What it reads. ERCOT posts a "60-Day DAM Disclosure Reports" zip (EMIL NP3-966-ER, report type 13051) each day, for
the operating day 60 days before. One of its files, 60d_DAM_ESR_Data-DD-MMM-YY.csv, has a row for each Energy Storage
Resource and hour: the resource's offer, its limits (HSL, LSL), its awarded energy and the price at its settlement
point, and its award and the clearing price of each Ancillary Service. This script keeps the award columns and the
limits and leaves the offer curve out.

The run stops before writing past the ceiling: whole days are kept, in order, while they fit.
"""
import argparse
import datetime as dt
import glob
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
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

REPORT_TYPE = 13051
LIST = f"https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId={REPORT_TYPE}"
FILE = "https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId={doc}"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CEILING = 300_000
LAG_DAYS = 60
OUT_DIR = os.path.join(ROOT, "warehouse", "output", "analysis_internal")
KEEP = ["Delivery Date", "Hour Ending", "QSE", "DME", "Resource Name", "Resource Type", "HSL", "LSL", "Resource Status", "Awarded Quantity", "Settlement Point Name",
        "Energy Settlement Point Price", "RegUp Awarded", "RegUp MCPC", "RegDown Awarded", "RegDown MCPC", "RRSPFR Awarded", "RRSFFR Awarded", "RRSUFR Awarded", "RRS MCPC",
        "ECRSSD Awarded", "ECRS MCPC", "NonSpin Awarded", "NonSpin MCPC"]


def esr_frame(content):
    """The ESR day-ahead file of one disclosure zip: (the file's name, its rows with the columns kept, every column it has)."""
    z = zipfile.ZipFile(io.BytesIO(content))
    names = [n for n in z.namelist() if re.search(r"60d_DAM_ESR_Data", n)]
    if len(names) != 1:
        raise ValueError(f"the zip holds {len(names)} ESR data files: {z.namelist()}")
    df = pd.read_csv(io.BytesIO(z.read(names[0])))
    missing = [c for c in KEEP if c not in df.columns]
    if missing:
        raise ValueError(f"{names[0]} lacks the columns {missing}")
    return names[0], df[KEEP].copy(), list(df.columns), {n: z.getinfo(n).file_size for n in z.namelist()}


def wanted(docs, month):
    """The documents whose operating day (the day published less 60) is in the month: [(operating day, document)]."""
    out = []
    for d in docs:
        published = dt.date.fromisoformat(d["PublishDate"][:10])
        day = published - dt.timedelta(days=LAG_DAYS)
        if day.strftime("%Y-%m") == month:
            out.append((day, d))
    return sorted(out, key=lambda x: x[0])


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERCOT 60-day DAM disclosure: the storage resources' day-ahead awards of one month (a sample)")
    ap.add_argument("--month", required=True, help="YYYY-MM, a month whose days are all 60 days old")
    ap.add_argument("--from-dir", help="read the zips saved in this directory by an earlier run; no request")
    a = ap.parse_args(argv)
    os.makedirs(OUT_DIR, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc)
    run_id = now.strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(OUT_DIR, f"ercot_disclosure_sample_{run_id}.log"))
    frames, files, notes, requests_made = [], [], [], 0
    if a.from_dir:
        zips = sorted(glob.glob(os.path.join(a.from_dir, "*.zip")))
        sources = [(None, z, open(z, "rb").read()) for z in zips]
    else:
        if ip.paused("ercot"):
            raise SystemExit(ip.pause_line("ercot"))
        raw = os.path.join(ROOT, "warehouse", "raw", "ercot_60d_dam", run_id)
        os.makedirs(raw, exist_ok=True)
        r = requests.get(LIST, headers=UA, timeout=120)
        requests_made += 1
        r.raise_for_status()
        with open(os.path.join(raw, "doclist.json"), "w", encoding="utf-8") as f:
            f.write(r.text)
        docs = [x["Document"] for x in r.json()["ListDocsByRptTypeRes"]["DocumentList"]]
        want = wanted(docs, a.month)
        log(f"{LIST}: {len(docs)} documents listed, {docs[-1]['PublishDate'][:10]} to {docs[0]['PublishDate'][:10]}, {sum(int(d['ContentSize']) for d in docs):,} bytes; "
            f"{len(want)} for the operating days of {a.month}")
        sources = []
        for day, d in want:
            url = FILE.format(doc=d["DocID"])
            g = requests.get(url, headers=UA, timeout=300)
            requests_made += 1
            time.sleep(1)
            if g.status_code != 200:
                notes.append(f"{day}: HTTP {g.status_code} for {url}; the day is not in the sample")
                continue
            path = os.path.join(raw, d["ConstructedName"])
            with open(path, "wb") as f:
                f.write(g.content)
            sources.append((url, path, g.content))
    total = 0
    for url, path, content in sources:
        name, df, cols, sizes = esr_frame(content)
        days = sorted(set(df["Delivery Date"]))
        if len(days) != 1:
            raise ValueError(f"{name} holds {len(days)} delivery dates")
        day = dt.datetime.strptime(days[0], "%m/%d/%Y").date()
        if day.strftime("%Y-%m") != a.month:
            notes.append(f"{name}: delivery date {day} is not in {a.month}; not in the sample")
            continue
        if total + len(df) > CEILING:
            notes.append(f"{day}: its {len(df):,} rows would pass the ceiling of {CEILING:,} (at {total:,}); the sample stops before this day")
            break
        total += len(df)
        df.insert(0, "delivery_date", day.isoformat())
        df["source_url"] = url or os.path.basename(path)
        frames.append(df.drop(columns=["Delivery Date"]))
        files.append({"day": day.isoformat(), "file": name, "rows": int(len(df)), "zip_bytes": len(content), "esr_file_bytes": sizes[name], "columns_in_file": len(cols)})
        log(f"  {day}: {name}, {len(df):,} rows, {df['Resource Name'].nunique()} resources")
    if not frames:
        raise SystemExit("no day of the month was read; nothing written")
    t = pd.concat(frames, ignore_index=True)
    out = os.path.join(OUT_DIR, f"ercot_60d_dam_esr_awards_{a.month}.csv")
    with open(out, "w", encoding="utf-8", newline="") as f:
        for line in [
            f"Energy Research Warehouse (ERW): a SAMPLE for scoping, not a warehouse table (session 108). ERCOT 60-Day DAM Disclosure Reports (NP3-966-ER), "
            f"the file 60d_DAM_ESR_Data: Energy Storage Resources' day-ahead awards, operating days of {a.month}.",
            "One row per resource and hour ending (Central prevailing time, as ERCOT gives it). The award columns and the limits are kept as ERCOT names them; "
            "the offer curve columns are left out. MW for quantities, USD per MWh for the settlement point price, USD per MW for an MCPC.",
            f"Retrieved: {run_id} (UTC) by warehouse/analysis/ercot_disclosure_sample.py; {len(files)} days, {len(t):,} rows of a ceiling of {CEILING:,}.",
            f"Source: ERCOT, 60-Day DAM Disclosure Reports, {LIST}",
            "License: public. ERCOT's terms (https://www.ercot.com/help/terms): \"raw data provided in public portions of this website may be used, reproduced, "
            "and redistributed in compilations, charts, and analyses without maintaining such notices.\"",
            "Not in coverage, the archive, Redivis or Supabase.",
        ]:
            f.write("# " + line + "\n")
        t.to_csv(f, index=False, lineterminator="\n")
    meta = {"month": a.month, "run_id": run_id, "requests": requests_made, "days": files, "rows": int(len(t)), "ceiling": CEILING, "notes": notes, "table": os.path.relpath(out, ROOT).replace(os.sep, "/")}
    with open(os.path.join(OUT_DIR, f"ercot_60d_dam_esr_awards_{a.month}.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1)
    for n in notes:
        log("  " + n)
    log.close()
    print(f"{os.path.basename(out)}: {len(t):,} rows of {CEILING:,}, {len(files)} days, {t['Resource Name'].nunique()} resources; {requests_made} requests; {len(notes)} notes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
