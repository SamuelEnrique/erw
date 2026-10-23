#!/usr/bin/env python3
"""The Bureau of Reclamation's hydropower plants: each plant's installed capacity and its gross generation, plant
auxiliary use and net generation, a month, from October 2013 (session 2003, chain 056).

Energy Research Warehouse (ERW) connector. One series table from Reclamation's Power Resources Office workbook "Active
USBR Facilities, Operated and Maintained by Reclamation, Monthly and Annual Performance Data", linked from its Reports and
Data page:

    https://www.usbr.gov/power/data/data.html        (the page; the workbook's name carries its month, Plant_Data_MM_YYYY.xlsx)

    usbr_hydropower_monthly   entity usbr_plant:<facility>; variables installed_capacity (MW, Reclamation's kW over
                              1,000), gross_generation, auxiliary_use and net_generation (MWh, its kWh over 1,000); ts_utc
                              the month's first day; freq P1M; geo empty (the workbook gives no state); node the facility as
                              Reclamation names it; x_region Reclamation's region (MB, CGB, CPN, LCB, UCB, from the
                              workbook's annual sheet)

Net generation below zero (a month when the plant used more than it made) is kept as Reclamation writes it. The workbook's
annual sheet (fiscal years) is not written: its net generation is checked against the sum of each fiscal year's months
(October to September) and the count of years that agree is in the header. Reclamation's RISE (data.usbr.gov) was the
chain's first address: its robots file disallows /rise/api and the time series queries, the only ways its data are served
(session 2003).

A heading not as read, a facility in one sheet and not the other, a month not MM/YYYY, or an (entity, variable, ts_utc)
given twice stops the run; an empty cell has no row; nothing is filled. The data are provisional, as Reclamation says.

    python warehouse/connectors/usbr_power.py [--offline] [--out-dir DIR]

Ceiling: two requests (the page, fetched fresh to find the workbook's current name, and the workbook), saved in
warehouse/raw/usbr_power/ and reused offline. www.usbr.gov's robots file disallows only /pn-bin and /gp-bin. License:
public (a work of the U.S. government; the Department of the Interior's notice, as for BOEM, ONRR and BLM).
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "usbr_power"
SOURCE = "usbr:power_plant_data"
PAGE = "https://www.usbr.gov/power/data/data.html"
BASE_URL = "https://www.usbr.gov/power/data/"
TABLE = "usbr_hydropower_monthly"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
MONTHLY = ["Facility", "Reporting Date", "Installed Capacity (kW)", "Gross Generation (kWh)", "Plant Auxiliary Use (kWh)", "Net Generation (kWh)"]
ANNUAL = ["Region", "Facility", "Units", "Fiscal Year", "Plant Capacity (kWh)", "Gross Generation (kWh)", "Net Generation (kWh)"]
VARS = [("Installed Capacity (kW)", "installed_capacity", "MW"), ("Gross Generation (kWh)", "gross_generation", "MWh"),
        ("Plant Auxiliary Use (kWh)", "auxiliary_use", "MWh"), ("Net Generation (kWh)", "net_generation", "MWh")]
X_COLS = ["x_region"]


def text(v):
    return "" if v is None or (isinstance(v, float) and pd.isna(v)) else re.sub(r"\s+", " ", str(v)).strip()


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def workbook_name(page_html):
    names = sorted(set(re.findall(r'href="(Plant_Data_(\d{2})_(\d{4})\.xlsx)"', page_html)), key=lambda m: (m[2], m[1]))
    if not names:
        raise RuntimeError("no Plant_Data_MM_YYYY.xlsx linked from the page")
    return names[-1][0]


def sheet(d, heads, name):
    """The rows under the heading row (the first whose cells are the headings)."""
    for i in range(min(len(d), 15)):
        if [text(v) for v in d.iloc[i, :len(heads)].tolist()] == heads:
            body = d.iloc[i + 1:, :len(heads)].copy()
            body.columns = heads
            return body[body[heads[0]].map(text) != ""]
    raise RuntimeError(f"{name}: headings not as read: expected {heads}")


def build(monthly, annual, base):
    m, a = sheet(monthly, MONTHLY, "Monthly Generation"), sheet(annual, ANNUAL, "Annual Plant Generation")
    m["Facility"] = m["Facility"].map(text)
    a["Facility"] = a["Facility"].map(text)
    region = dict(zip(a["Facility"], a["Region"].map(text)))
    if set(m["Facility"]) != set(a["Facility"]):
        raise RuntimeError(f"facilities differ between the sheets: {sorted(set(m['Facility']) ^ set(a['Facility']))[:5]}")
    out = []
    for _, r in m.iterrows():
        when = text(r["Reporting Date"])
        mm = re.fullmatch(r"(\d{2})/(\d{4})", when)
        if not mm:
            raise RuntimeError(f"a month not MM/YYYY: {when!r} ({r['Facility']})")
        ts = f"{mm.group(2)}-{mm.group(1)}-01T00:00:00Z"
        for col, var, unit in VARS:
            v = pd.to_numeric(r[col], errors="coerce")
            if pd.isna(v):
                continue
            out.append(dict(base, entity=f"usbr_plant:{slug(r['Facility'])}", variable=var, ts_utc=ts, value=float(v) / 1000, unit=unit,
                            freq="P1M", geo="", market="", node=r["Facility"], x_region=region[r["Facility"]]))
    s = pd.DataFrame(out)
    if s.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError(f"an (entity, variable, ts_utc) given twice: {s[s.duplicated(['entity', 'variable', 'ts_utc'])].entity.head(3).tolist()}")
    # the annual sheet's net generation against the sum of each fiscal year's months (October to September)
    net = s[s.variable == "net_generation"].copy()
    ts = pd.to_datetime(net.ts_utc)
    net["fy"] = ts.dt.year + (ts.dt.month >= 10).astype(int)
    sums = net.groupby(["node", "fy"]).value.sum()
    checked = agree = 0
    for _, r in a.iterrows():
        v = pd.to_numeric(r["Net Generation (kWh)"], errors="coerce")
        key = (r["Facility"], int(r["Fiscal Year"]))
        if pd.isna(v) or key not in sums.index:
            continue
        checked += 1
        agree += abs(sums[key] - v / 1000) <= max(1.0, abs(v / 1000) * 0.001)
    return s, checked, agree


def main(argv=None):
    ap = argparse.ArgumentParser(description="Reclamation's hydropower plants: monthly generation and capacity")
    ap.add_argument("--offline", action="store_true", help="the saved page and workbook only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=60)
        name = workbook_name(page.decode("utf-8", errors="replace"))
        url = BASE_URL + name
        content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=120)
        base = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        book = pd.read_excel(io.BytesIO(content), sheet_name=None, header=None)
        for need in ("Monthly Generation", "Annual Plant Generation"):
            if need not in book:
                raise RuntimeError(f"sheet not found: {need}")
        generated = text(book["Monthly Generation"].iloc[1, 0])
        s, checked, agree = build(book["Monthly Generation"], book["Annual Plant Generation"], base)
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        neg = int(((s.variable == "net_generation") & (s.value < 0)).sum())
        head = [
            "Energy Research Warehouse (ERW): U.S. Bureau of Reclamation, Power Resources Office, Active USBR Facilities, Operated and Maintained by "
            "Reclamation, Monthly and Annual Performance Data: each hydropower plant's installed capacity and gross generation, plant auxiliary use and "
            "net generation, a month (session 2003)",
            "Shape: series (docs/datastandard.md v0). entity usbr_plant:<facility>; variables installed_capacity (MW, Reclamation's kW over 1,000), "
            "gross_generation, auxiliary_use, net_generation (MWh, its kWh over 1,000); freq P1M; ts_utc the month's first day; geo empty (the workbook "
            "gives no state); node the facility; x_region Reclamation's region.",
            f"{s.entity.nunique()} plants, {s.ts_utc.min()[:7]} to {s.ts_utc.max()[:7]}. {neg} months of net generation below zero, kept as written. "
            f"The annual sheet's net generation: {agree} of {checked} plant fiscal years equal the sum of their months (within 0.1 percent); the sheet "
            "is not written. Reclamation's note: 'Facility data is considered PROVISIONAL and is subject to revision.' Workbook: "
            f"{generated}. An empty cell has no row. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/usbr_power.py; the workbook retrieved {base['retrieved_at']}, last modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Bureau of Reclamation, Power Resources Office, Reports and Data, {PAGE}",
            f"  access: {url}",
            'License: public (a work of the U.S. government; cite "U.S. Bureau of Reclamation, Power Resources Office").',
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s)} rows, {s.entity.nunique()} plants; annual check {agree} of {checked}; {neg} negative net months")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Bureau of Reclamation (USBR)",
                                    report="Active USBR Facilities, Operated and Maintained by Reclamation, Monthly and Annual Performance Data",
                                    report_url=PAGE, document_list=BASE_URL, license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
