#!/usr/bin/env python3
"""The Department of the Treasury's Section 1603 awards: the payments in lieu of investment tax credits that funded the
first wave of U.S. wind and solar after 2009, each award's business, state, technology, amount and date (session 2112,
chain 069).

Energy Research Warehouse (ERW) connector. One events table from the program's awardee list, linked from

    https://home.treasury.gov/policy-issues/financial-markets-financial-institutions-and-fiscal-service/1603-program-payments-for-specified-energy-property-in-lieu-of-tax-credits

    treasury_1603_awards   event_id treasury_1603:<a hash of the row's five fields>; event_date the award date; event_type
               grant_award; parties the business as the Treasury names it; entity_ids US-<state or territory>; mw, price
               and currency empty (the list gives no capacity, and the award is not a price per MWh); status awarded;
               x_state; x_technology as the Treasury names it; x_funded_usd the amount funded in dollars; x_as_of the
               date the list's title gives

The list's sheet must hold a title row naming "Awardees as of <date>", a header row Business Name, State, Technology,
Funded, Award Date, one row an award, and a Total row; the awards must sum to the Total exactly, or the run stops. One
award date is an Excel serial number in the Treasury's file and is read as one (counted in the header). A row given
twice, a funded amount that is not a whole number of dollars, a date that does not read or a state that is not two
letters stops the run. The Treasury's page reports "over $26 billion" for "109,766 clean energy projects": the list
holds awards, not projects, and an award can cover several projects. Nothing is filled.

    python warehouse/connectors/treasury_1603.py [--offline] [--out-dir DIR]

Ceiling: two requests (the program page, read for the list's address, and the list; both saved in
warehouse/raw/treasury_1603/ and reused offline; asked again unless --offline). home.treasury.gov's robots file allows /. License: not settled (the
Treasury's site states no terms of reuse; session 2111, reads 247 and 248; no verdict row yet), so internal in
sources.csv until a ruling.
"""

import argparse
import datetime as dt
import hashlib
import io
import os
import re
import sys
import traceback
import urllib.parse

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "treasury_1603"
SOURCE = "treasury:section_1603_awards"
HOST = "home.treasury.gov"
PAGE = ("https://home.treasury.gov/policy-issues/financial-markets-financial-institutions-and-fiscal-service/"
        "1603-program-payments-for-specified-energy-property-in-lieu-of-tax-credits")
TABLE = "treasury_1603_awards"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
EVENT_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source", "source_url"]
X_COLS = ["x_state", "x_technology", "x_funded_usd", "x_as_of"]
HEAD = ["Business Name", "State", "Technology", "Funded", "Award Date"]
EXCEL_EPOCH = dt.date(1899, 12, 30)


def list_url(page):
    hits = sorted(set(h for h in re.findall(r'href="?([^" >]+\.xlsx)', page) if "awarded" in h.lower()))
    if len(hits) != 1:
        raise RuntimeError(f"the page links not one awardee list: {hits}")
    return urllib.parse.urljoin(PAGE, hits[0])


def as_of(title):
    m = re.search(r"Awardees as of (\w+ \d{1,2}, \d{4})", re.sub(r"\s+", " ", str(title)))
    if not m:
        raise RuntimeError(f"the title names no 'Awardees as of' date: {str(title)[:160]!r}")
    return dt.datetime.strptime(m.group(1), "%B %d, %Y").date().isoformat()


def day(x, where, serials):
    if isinstance(x, dt.datetime):
        return x.date().isoformat()
    if isinstance(x, int) and not isinstance(x, bool) and 30000 < x < 60000:
        serials.append(where)
        return (EXCEL_EPOCH + dt.timedelta(days=x)).isoformat()
    raise RuntimeError(f"{where}: a date that does not read: {x!r}")


def parse(content, base):
    v = pd.read_excel(io.BytesIO(content), sheet_name=0, header=None, dtype=object, keep_default_na=False)
    when = as_of(v.iat[0, 0])
    h = [i for i in range(min(len(v), 10)) if [str(c).strip() for c in v.iloc[i, :5]] == HEAD]
    if len(h) != 1:
        raise RuntimeError(f"no single header row {HEAD}")
    out, seen, serials, total = [], set(), [], None
    for i in range(h[0] + 1, len(v)):
        name, st, tech, funded, date = (v.iat[i, j] for j in range(5))
        name, st, tech = str(name).strip(), str(st).strip(), str(tech).strip()
        if name == "Total":
            total = funded
            break
        if not any(str(c).strip() for c in (name, st, tech, funded, date)):
            continue
        where = f"row {i + 1} ({name})"
        if not re.fullmatch(r"[A-Z]{2}", st):
            raise RuntimeError(f"{where}: a state that is not two letters: {st!r}")
        if isinstance(funded, bool) or not isinstance(funded, (int, float)) or float(funded) != int(funded):
            raise RuntimeError(f"{where}: a funded amount that is not a whole number of dollars: {funded!r}")
        d = day(date, where, serials)
        key = (name, st, tech, int(funded), d)
        if key in seen:
            raise RuntimeError(f"{where}: an award given twice")
        seen.add(key)
        eid = "treasury_1603:" + hashlib.sha1("|".join(map(str, key)).encode("utf-8")).hexdigest()[:12]
        out.append(dict(base, event_id=eid, event_date=d, event_type="grant_award", parties=name, entity_ids=f"US-{st}", mw="", price="",
                        currency="", status="awarded", x_state=st, x_technology=tech, x_funded_usd=int(funded), x_as_of=when))
    if total is None:
        raise RuntimeError("no Total row")
    s = sum(r["x_funded_usd"] for r in out)
    if s != int(total):
        raise RuntimeError(f"the awards sum to {s}, the Total row is {total}")
    if len({r["event_id"] for r in out}) != len(out):
        raise RuntimeError("two awards share an event_id")
    return out, when, serials, int(total)


def main(argv=None):
    ap = argparse.ArgumentParser(description="The Treasury's Section 1603 awards")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
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
        if ip.paused(CONNECTOR) or ip.paused_host(HOST):
            raise RuntimeError(f"{HOST} is paused (warehouse/metadata/paused_sources.csv): no request made")
        page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120, pause=1)
        url = list_url(page.decode("utf-8", errors="replace"))
        log(f"  awardee list: {url}")
        content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120, pause=1)
        base = dict(source=SOURCE, source_url=url)
        rows, when, serials, total = parse(content, base)
        t = pd.DataFrame(rows)
        cols = EVENT_COLS + X_COLS
        t = t[cols].sort_values(["event_date", "x_state", "parties", "event_id"]).reset_index(drop=True)
        head = [
            f"Energy Research Warehouse (ERW): U.S. Department of the Treasury, Section 1603 Payments for Specified Energy Property in Lieu "
            f"of Tax Credits, the awardee list as of {when}: {len(t):,} awards, USD {total:,} funded, {t.event_date.min()} to "
            f"{t.event_date.max()} (session 2112)",
            "Shape: events (docs/datastandard.md v0). event_id treasury_1603:<hash>; event_date the award date; event_type grant_award; parties "
            "the business as named; entity_ids US-<state>; mw, price, currency empty; status awarded; x_state; x_technology as named; "
            "x_funded_usd the amount funded (USD); x_as_of the list's date.",
            f"Checked as read: the awards sum to the list's Total exactly (USD {total:,}). Dates the Treasury's file holds as Excel serial "
            f"numbers, read as such: {len(serials)} ({'; '.join(serials) or 'none'}). The list holds awards, not projects: the Treasury's page "
            "counts 109,766 projects funded by over USD 26 billion. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/treasury_1603.py; the list retrieved {rec.get('retrieved_at') or ''}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Department of the Treasury, 1603 Program, {PAGE}",
            f"  access: {url}",
            "License: not settled (the Treasury's site states no terms of reuse, session 2111; no verdict yet), held internal until a ruling. "
            "Cite the U.S. Department of the Treasury.",
        ]
        ip.write_snapshot(t, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{TABLE}: {len(t)} awards, USD {total:,}; serial dates {len(serials)}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Department of the Treasury",
                                    report="Section 1603 Program: the awardee list", report_url=PAGE, document_list=PAGE,
                                    license="internal", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
