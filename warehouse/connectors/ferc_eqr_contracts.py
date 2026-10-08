#!/usr/bin/env python3
"""FERC Electric Quarterly Reports: the contracts of one quarter (session 83; scoped in session 81).

Energy Research Warehouse (ERW) connector. Public utilities, and non-public utilities with more than a de minimis
market presence, file an Electric Quarterly Report (EQR) with FERC each quarter: the contractual terms of their
agreements for jurisdictional services (contracts), and what was delivered and billed in the quarter (transactions).
This reads the contracts only, and writes one internal events table, ferc_eqr_contracts: one row per product of an
agreement in force, as the seller filed it.

Source. FERC's EQR report viewer, https://eqrreportviewer.ferc.gov/ (Downloads, Quarterly Filings, All Companies), gives
one zip per quarter, CSV_<year>_Q<q>.zip, about 3.6 GB, holding one small zip per filing; each filing holds four CSV
files (ident, contracts, transactions, indexPub). The address carries a key the viewer page gives, so it is read from
the page each run. The server answers range requests: the quarter's list of filings is read first (no data rows), then
one request per filing, a filing at a time. From each filing only the contracts file is read, and from the ident file
only the filer's company identifier, name and quarter. The transactions are not parsed and not kept; the filers'
contact persons (names, telephone numbers, email addresses in the ident file) are never read into a row or a raw file.

    python warehouse/connectors/ferc_eqr_contracts.py --quarter 2026_Q2            # the approved pull (session 83)
    python warehouse/connectors/ferc_eqr_contracts.py --quarter 2026_Q2 --list     # the filings and their sizes; no data
    python warehouse/connectors/ferc_eqr_contracts.py --quarter 2026_Q2 --limit 50 # a trial: the first 50 filings, a
                                                                                   # scratch file under runs/, no table

Ceiling: 400,000 contract rows (Samuel's approval, session 83). The count is kept filing by filing; a filing that would
pass the ceiling is not added, the run stops, and nothing is written: a table cut at an arbitrary filing would look
complete and not be. The raw contract files already fetched are kept, so a rerun with a ruling does not fetch them again.

One row per contract row. A filer files a row per product of an agreement (energy, capacity, a year's price), so an
agreement has one or several rows. When a company has more than one filing in the quarter's file (a refiling), the
newest filing is the company's and the earlier ones are counted and left out. A row whose execution date cannot be
read is left out and counted; so is a row whose execution date is outside the dates the standard can hold (1677 to
2262: a filer typed 2915); nothing is filled and no date is corrected. An execution date after the quarter filed for
that the standard can hold (July 2026, or 2101) stays, as filed.

The events shape (docs/datastandard.md):
    event_id     ferc_eqr:<quarter>:<company identifier>:<contract_unique_id>:<n>, n the row's place among the rows of
                 that contract id in the filing (FERC's contract id repeats across a contract's products)
    event_date   the contract's execution date
    event_type   contract
    parties      seller;buyer, as filed
    mw           the quantity when its units are MW; price: the rate when its units are $/MWH; currency USD with a price
    status       terminated when an actual termination date is filed, else in_force
    x_*          every other column of FERC's contract file, under its own name, and x_company_id, x_filing, x_quarter

License: internal (session 83's instruction). The filings are public (FERC publishes them to make the data available to
the public: its notice of 17 February 2026, 91 FR 7279); FERC's own license statement could not be read by this machine
(ferc.gov answers automated requests with HTTP 403), so the table stays internal until a person has read it.
"""

import argparse
import csv
import datetime as dt
import hashlib
import html
import io
import json
import os
import re
import struct
import sys
import time
import traceback
import zipfile
import zlib

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "ferc_eqr_contracts"
SOURCE = "ferc:eqr"
VIEWER = "https://eqrreportviewer.ferc.gov/"
CEILING = 400_000
# Session 125: an approved pull of three more quarters, a filing at a time, 800,000 contract rows in all. The ceiling of
# one run stays as it was; PULL_CEILING is the pull's, counted over this run and the quarters named with --also.
PULL_CEILING = 800_000
PAUSE = 0.2   # seconds between two filings asked of FERC's server
# The earlier quarters of the approved pull go to a table of their own, in the same shape: ferc_eqr_contracts stays one
# quarter, the newest, which is what the page, the buyers' tables and the live set read. Every agreement in force is
# filed again each quarter, so one table of four quarters would hold most contracts four times.
HISTORY = "ferc_eqr_contracts_history"
UA = {"User-Agent": "Mozilla/5.0 (ERW research; github.com/SamuelEnrique/erw)"}
# FERC's contract columns, in the file's order (the header of every contracts file is checked against this)
FERC_COLS = ["contract_unique_id", "seller_company_name", "customer_company_name", "contract_affiliate", "ferc_tariff_reference",
             "contract_service_agreement_id", "contract_execution_date", "commencement_date_of_contract_term",
             "contract_termination_date", "actual_termination_date", "extension_provision_description", "class_name", "term_name",
             "increment_name", "increment_peaking_name", "product_type_name", "product_name", "quantity", "units", "rate",
             "rate_minimum", "rate_maximum", "rate_description", "rate_units", "point_of_receipt_balancing_authority",
             "point_of_receipt_specific_location", "point_of_delivery_balancing_authority", "point_of_delivery_specific_location",
             "begin_date", "end_date"]
X_COLS = [c for c in FERC_COLS if c not in ("contract_execution_date",)]
EVENT_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source", "source_url"]
COLS = EVENT_COLS + ["x_" + c for c in X_COLS] + ["x_company_id", "x_filing", "x_quarter"]


class RangeFile(io.RawIOBase):
    """A remote file read by HTTP range requests; only the bytes asked for are fetched."""

    def __init__(self, url, block=1 << 20):
        self.url, self.block, self.pos = url, block, 0
        self.s = requests.Session()
        h = self.s.head(url, headers=UA, timeout=120)
        h.raise_for_status()
        if h.headers.get("Accept-Ranges", "").lower() != "bytes":
            raise RuntimeError("the server no longer answers range requests; the quarter cannot be read a filing at a time")
        self.size = int(h.headers["Content-Length"])
        self.last_modified = h.headers.get("Last-Modified", "")
        self.cache, self.requests, self.bytes = {}, 1, 0

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, off, whence=0):
        self.pos = off if whence == 0 else self.pos + off if whence == 1 else self.size + off
        return self.pos

    def get(self, a, b, tries=4):
        for k in range(tries):
            try:
                r = self.s.get(self.url, headers={**UA, "Range": f"bytes={a}-{b - 1}"}, timeout=600)
                if r.status_code != 206 or len(r.content) != b - a:
                    raise RuntimeError(f"range request answered {r.status_code} with {len(r.content)} of {b - a} bytes")
                self.requests += 1
                self.bytes += len(r.content)
                return r.content
            except Exception:
                if k == tries - 1:
                    raise
                time.sleep(5 * (k + 1))

    def prefetch(self, a, b):
        a = (a // self.block) * self.block
        data = self.get(a, min(b, self.size))
        for i in range(0, len(data), self.block):
            self.cache[(a + i) // self.block] = data[i:i + self.block]

    def read(self, n=-1):
        if n < 0:
            n = self.size - self.pos
        out = bytearray()
        while n > 0 and self.pos < self.size:
            k = self.pos // self.block
            if k not in self.cache:
                self.cache[k] = self.get(k * self.block, min((k + 1) * self.block, self.size))
            take = self.cache[k][self.pos - k * self.block:self.pos - k * self.block + n]
            if not take:
                break
            out += take
            self.pos += len(take)
            n -= len(take)
        return bytes(out)

    def readinto(self, b):
        d = self.read(len(b))
        b[:len(d)] = d
        return len(d)


def quarter_url(quarter):
    """The quarter's CSV file, as the viewer's Downloads tab lists it (the address holds a key the page gives)."""
    s = requests.Session()
    page = s.get(VIEWER, headers=UA, timeout=120).text
    f = {}
    for m in re.finditer(r'<input[^>]*type="hidden"[^>]*>', page):
        n, v = re.search(r'name="([^"]*)"', m.group(0)), re.search(r'value="([^"]*)"', m.group(0))
        if n:
            f[n.group(1)] = html.unescape(v.group(1)) if v else ""
    f["TabContainerReportViewer_ClientState"] = '{"ActiveTabIndex":1,"TabEnabledState":[true,true],"TabWasLoadedOnceState":[false,false]}'
    f["__EVENTTARGET"], f["__EVENTARGUMENT"] = "TabContainerReportViewer", "activeTabChanged:1"
    r = s.post(VIEWER, data=f, headers=UA, timeout=120)
    r.raise_for_status()
    m = re.search(r'href="(https://eqrreportviewer\.ferc\.gov/DownloadRepositoryProd/[^"]*/BulkNew/CSV/CSV_%s\.zip)"' % re.escape(quarter), r.text)
    if not m:
        raise RuntimeError(f"the viewer's Downloads tab lists no CSV_{quarter}.zip")
    return html.unescape(m.group(1))


def public_url(url):
    """The address without its key, for a row's source_url (the key is the viewer's, not a secret, but it changes)."""
    return re.sub(r"/DownloadRepositoryProd/[^/]+/", "/DownloadRepositoryProd/<key from the viewer's Downloads tab>/", url)


def listing(f):
    f.prefetch(max(0, f.size - (8 << 20)), f.size)  # the end of the file, where the list of members is
    z = zipfile.ZipFile(io.BufferedReader(f, buffer_size=1 << 20))
    return [(i.filename, i.compress_type, i.compress_size, i.file_size, i.header_offset) for i in z.infolist()]


def member(f, name, comp_type, comp_size, offset):
    """One filing's zip, by one range request (its local header and its data)."""
    blob = f.get(offset, min(f.size, offset + 30 + 2048 + comp_size))
    sig, _, _, _, _, _, _, _, _, nlen, xlen = struct.unpack("<IHHHHHIIIHH", blob[:30])
    if sig != 0x04034B50:
        raise RuntimeError(f"{name}: no local header at {offset}")
    data = blob[30 + nlen + xlen:30 + nlen + xlen + comp_size]
    if len(data) != comp_size:
        raise RuntimeError(f"{name}: {len(data)} of {comp_size} bytes")
    return zlib.decompress(data, -15) if comp_type == 8 else data


def read_filing(inner):
    """(contract rows as lists, the contracts file's bytes, company identifier, company name, filing quarter) of one
    filing's zip. Only the contracts file and three columns of the ident file are read."""
    z = zipfile.ZipFile(io.BytesIO(inner))
    rows, raw, cid, cname, fq = [], b"", "", "", ""
    for info in z.infolist():
        low = info.filename.lower()
        if low.endswith("_contracts.csv"):
            raw = z.read(info)
            recs = list(csv.reader(io.StringIO(raw.decode("utf-8-sig", errors="replace"))))
            if recs:
                if [c.strip().lower() for c in recs[0]] != FERC_COLS:
                    raise RuntimeError(f"{info.filename}: columns {recs[0][:6]}... are not FERC's contract columns")
                rows = [r for r in recs[1:] if any(c.strip() for c in r)]
        elif low.endswith("_ident.csv"):
            recs = list(csv.reader(io.StringIO(z.read(info).decode("utf-8-sig", errors="replace"))))
            if len(recs) > 1:
                h = [c.strip().lower() for c in recs[0]]
                first = recs[1]
                cid = first[h.index("company_identifier")].strip() if "company_identifier" in h else ""
                cname = first[h.index("company_name")].strip() if "company_name" in h else ""
                fq = first[h.index("filing_quarter")].strip() if "filing_quarter" in h else ""
    return rows, raw, cid, cname, fq


def ymd(s):
    s = (s or "").strip()
    if re.fullmatch(r"\d{8}", s):
        try:
            return dt.date(int(s[:4]), int(s[4:6]), int(s[6:])).isoformat()
        except ValueError:
            return None
    return None


# The dates the standard can hold: the validator, the loader and every reader parse a date with pandas, whose
# timestamps run from 1677-09-22 to 2262-04-11. A filer's execution date outside them (2915-01-01 is filed) is a typing
# error no table can carry as a date: the row is left out and counted, like a row with no readable date.
DATE_MIN, DATE_MAX = "1677-09-22", "2262-04-11"


def number(s):
    try:
        v = float(str(s).replace(",", "").strip())
        return v if v == v and abs(v) != float("inf") else None
    except ValueError:
        return None


def events(filings, quarter, url, retrieved):
    """The table's rows from the filings read: [(filing, company id, company name, contract rows)], the newest filing of
    each company only. Returns (rows, counts)."""
    newest = {}
    for name, cid, cname, rows in filings:
        key = cid or ("name:" + cname) or name
        order = tuple(int(x) for x in re.findall(r"\d+", name)[-2:])
        if key not in newest or order > newest[key][0]:
            newest[key] = (order, name, cid, cname, rows)
    out, undated, beyond, superseded = [], 0, [], len(filings) - len(newest)
    q = quarter.replace("_", "")
    for _, name, cid, cname, rows in sorted(newest.values(), key=lambda t: t[1]):
        seen = {}
        for r in rows:
            r = (r + [""] * len(FERC_COLS))[:len(FERC_COLS)]
            d = dict(zip(FERC_COLS, (c.strip() for c in r)))
            when = ymd(d["contract_execution_date"])
            n = seen[d["contract_unique_id"]] = seen.get(d["contract_unique_id"], 0) + 1
            if when is None:
                undated += 1
                continue
            if not DATE_MIN <= when <= DATE_MAX:
                beyond.append(when)
                continue
            rate, qty = number(d["rate"]), number(d["quantity"])
            price = rate if rate is not None and d["rate_units"].upper() == "$/MWH" else None
            e = dict(event_id=f"ferc_eqr:{q}:{cid or hashlib.sha256(cname.encode()).hexdigest()[:10]}:{d['contract_unique_id']}:{n}",
                     event_date=when, event_type="contract",
                     parties=";".join(p.replace(";", ",") for p in (d["seller_company_name"], d["customer_company_name"]) if p),
                     entity_ids="", mw=qty if qty is not None and d["units"].upper() == "MW" else "",
                     price=price if price is not None else "", currency="USD" if price is not None else "",
                     status="terminated" if ymd(d["actual_termination_date"]) else "in_force", source=SOURCE, source_url=public_url(url))
            for c in X_COLS:
                e["x_" + c] = d[c]
            e.update(x_company_id=cid, x_filing=name, x_quarter=quarter)
            out.append(e)
    return out, dict(companies=len(newest), superseded_filings=superseded, undated_rows=undated, out_of_range_rows=len(beyond),
                     out_of_range_dates=sorted(set(beyond)))


def main(argv=None):
    ap = argparse.ArgumentParser(description="FERC EQR: the contracts of one quarter")
    ap.add_argument("--quarter", required=True, help="for example 2026_Q2")
    ap.add_argument("--list", action="store_true", help="print the quarter's filings and their sizes; fetch no data")
    ap.add_argument("--limit", type=int, help="a trial: the first N filings, written to runs/, no table")
    ap.add_argument("--ceiling", type=int, default=CEILING)
    ap.add_argument("--fetch-only", action="store_true", help="session 125: fetch the quarter's contract files to warehouse/raw and stop; no table is written "
                    "(no data lock is needed). A later run of the quarter reads them from disk and writes the table")
    ap.add_argument("--history", action="store_true", help=f"session 125: write the quarter to {HISTORY}, the table of the quarters before the newest")
    ap.add_argument("--also", nargs="*", default=[], metavar="YYYY_Qn", help="session 125: the other quarters of the same approved pull; the contract rows already "
                    f"fetched for them count toward its ceiling of {PULL_CEILING:,}")
    args = ap.parse_args(argv)
    if ip.paused("ferc"):
        print("ferc is a paused publisher (warehouse/metadata/paused_sources.csv): no request is made", file=sys.stderr)
        return 1
    if not re.fullmatch(r"\d{4}_Q[1-4]", args.quarter):
        ap.error("--quarter is YYYY_Qn")
    if args.ceiling > CEILING:
        ap.error(f"the approved ceiling is {CEILING:,} rows")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"ferc_eqr_contracts_{run_id}.log"))
    results = []
    try:
        url = quarter_url(args.quarter)
        f = RangeFile(url)
        members = listing(f)
        log(f"ERW ferc_eqr_contracts run {run_id}; {args.quarter}: {f.size:,} bytes, {len(members):,} filings, Last-Modified {f.last_modified}; "
            f"ceiling {args.ceiling:,} contract rows")
        print(f"{args.quarter}: {f.size:,} bytes, {len(members):,} filings (the list read with {f.requests} requests, {f.bytes:,} bytes)")
        if args.list:
            sizes = sorted(m[3] for m in members)
            print(f"a filing's zip: median {sizes[len(sizes) // 2]:,} bytes, largest {sizes[-1]:,}")
            return 0
        raw_dir = os.path.join(ip.RAW_DIR, NAME, args.quarter)
        os.makedirs(raw_dir, exist_ok=True)
        index_path = os.path.join(raw_dir, "index.json")
        index = json.load(open(index_path, encoding="utf-8")) if os.path.exists(index_path) else {}
        todo = members[:args.limit] if args.limit else members
        filings, n_rows, t0 = [], 0, time.time()
        prior = 0
        for q in args.also:
            p = os.path.join(ip.RAW_DIR, NAME, q, "index.json")
            if q != args.quarter and os.path.exists(p):
                prior += sum(m["rows"] for m in json.load(open(p, encoding="utf-8")).values())
        if args.also:
            log(f"  the approved pull's other quarters ({', '.join(args.also)}) hold {prior:,} contract rows; its ceiling is {PULL_CEILING:,}")
        unreadable = []   # session 125: filings in the quarter's file that are not a zip file, read twice; left out and counted
        for k, (name, ctype, csize, fsize, off) in enumerate(todo, 1):
            raw_path = os.path.join(raw_dir, name + ".contracts.csv")
            if name in index and index[name].get("unreadable"):
                unreadable.append(name)   # found unreadable by an earlier run of this quarter: not asked for again, not a filing read
                continue
            if name in index and (index[name]["rows"] == 0 or os.path.exists(raw_path)):
                meta = index[name]  # fetched by an earlier run of this quarter: the contracts file is on disk
                raw = open(raw_path, "rb").read() if meta["rows"] else b""
                recs = list(csv.reader(io.StringIO(raw.decode("utf-8-sig", errors="replace"))))
                rows = [r for r in recs[1:] if any(c.strip() for c in r)]
                cid, cname = meta["company_id"], meta["company_name"]
            else:
                try:
                    rows, raw, cid, cname, fq = read_filing(member(f, name, ctype, csize, off))
                except zipfile.BadZipFile:
                    # 2025 Q4 holds a filing that is not a zip file. It is asked for once more (a broken read would differ);
                    # if it is the same again it is the source's, and the filing is left out, named in the log and counted
                    # in the header. Nothing is put in its place.
                    time.sleep(PAUSE)
                    blob = member(f, name, ctype, csize, off)
                    try:
                        rows, raw, cid, cname, fq = read_filing(blob)
                    except zipfile.BadZipFile:
                        log(f"  {name}: not a zip file in two reads (compression method {ctype}, {len(blob):,} bytes, sha256 {hashlib.sha256(blob).hexdigest()[:16]}, beginning {blob[:8].hex()}); "
                            "the filing is left out and counted")
                        index[name] = dict(company_id="", company_name="", filing_quarter="", rows=0, zip_bytes=fsize, sha256="", unreadable=True,
                                           retrieved_at=ip.utc_iso(pd.Timestamp.now(tz="UTC")))
                        json.dump(index, open(index_path, "w", encoding="utf-8"))
                        unreadable.append(name)
                        time.sleep(PAUSE)
                        continue
                time.sleep(PAUSE)   # a filing at a time, and a breath between two
                if rows:
                    with open(raw_path, "wb") as out:
                        out.write(raw)  # the contracts file as FERC serves it; nothing else of the filing is kept
                index[name] = dict(company_id=cid, company_name=cname, filing_quarter=fq, rows=len(rows), zip_bytes=fsize,
                                   sha256=hashlib.sha256(raw).hexdigest() if raw else "", retrieved_at=ip.utc_iso(pd.Timestamp.now(tz="UTC")))
                if k % 100 == 0:
                    json.dump(index, open(index_path, "w", encoding="utf-8"))
            if n_rows + len(rows) > args.ceiling:
                json.dump(index, open(index_path, "w", encoding="utf-8"))
                raise RuntimeError(f"the ceiling: {n_rows:,} contract rows after {k - 1:,} of {len(todo):,} filings, and {name} holds "
                                   f"{len(rows):,} more; stopped, nothing written (the contract files fetched so far are kept in "
                                   f"{os.path.relpath(raw_dir, ip.ROOT)})")
            if prior + n_rows + len(rows) > PULL_CEILING:
                json.dump(index, open(index_path, "w", encoding="utf-8"))
                raise RuntimeError(f"the approved pull's ceiling of {PULL_CEILING:,} contract rows: {prior:,} in its other quarters and {n_rows:,} in this one after "
                                   f"{k - 1:,} of {len(todo):,} filings, and {name} holds {len(rows):,} more; stopped, nothing written")
            n_rows += len(rows)
            filings.append((name, cid, cname, rows))
            if k % 250 == 0:
                log(f"  {k:,} of {len(todo):,} filings, {n_rows:,} contract rows, {f.requests:,} requests, {f.bytes / 1e6:,.0f} MB, "
                    f"{time.time() - t0:,.0f} s")
        json.dump(index, open(index_path, "w", encoding="utf-8"))
        if args.fetch_only:
            line = (f"{args.quarter}: fetched only: {len(filings):,} filings, {n_rows:,} contract rows, {f.requests:,} requests, {f.bytes / 1e9:.2f} GB, "
                    f"{time.time() - t0:,.0f} s; {len(unreadable):,} filings not a zip file and left out; no table written")
            log("  " + line)
            print(line)
            log.close()
            return 0
        retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        rows, counts = events(filings, args.quarter, url, retrieved)
        d = pd.DataFrame(rows, columns=COLS)
        if d["event_id"].duplicated().any():
            raise RuntimeError(f"{int(d['event_id'].duplicated().sum())} duplicate event ids; nothing written")
        log(f"  {len(filings):,} filings read, {n_rows:,} contract rows; {counts['companies']:,} companies, {counts['superseded_filings']:,} earlier "
            f"filings of a company left out, {counts['undated_rows']:,} rows without a readable execution date left out, "
            f"{counts['out_of_range_rows']:,} rows left out for an execution date no table can hold ({', '.join(counts['out_of_range_dates']) or 'none'}); {len(d):,} rows")
        header = [
            f"Energy Research Warehouse (ERW): FERC Electric Quarterly Reports, the contracts in force as filed for {args.quarter.replace('_', ' ')}",
            "Shape: events (docs/datastandard.md v0). One row per product of an agreement, as the seller filed it. event_date: the "
            "contract's execution date. event_type contract. parties: seller;buyer. mw: the quantity when its units are MW; price: the "
            "rate when its units are $/MWH (currency USD). status: terminated when an actual termination date is filed, else in_force. "
            "x_<column>: FERC's own contract columns, as filed; x_company_id FERC's company identifier of the filer; x_filing the "
            "filing's zip; x_quarter the quarter.",
            f"Counts: {len(members):,} filings in the quarter's file, {len(filings):,} read"
            + (f", {len(unreadable):,} left out because the file FERC serves for them is not a zip file (named in the run log)" if unreadable else "")
            + f"; {counts['companies']:,} companies; "
            f"{counts['superseded_filings']:,} earlier filings of a company left out (the newest filing is the company's); "
            f"{n_rows:,} contract rows read, {counts['undated_rows']:,} left out for an execution date that cannot be read and "
            f"{counts['out_of_range_rows']:,} for one outside {DATE_MIN} to {DATE_MAX}, the dates the standard can hold "
            f"({', '.join(counts['out_of_range_dates']) or 'none'}); ceiling "
            f"{args.ceiling:,} contract rows (session 83's approved pull). Transactions were not parsed; no contact person is in any row.",
            "Limits (session 81): no column says what technology a contract is for; about half the rows give their price as words "
            "(x_rate_description), not a number; every agreement in force is filed again each quarter, so new means executed "
            "recently (event_date), not present in this file. ERCOT's sales are outside FERC's jurisdiction and are not here.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/ferc_eqr_contracts.py; the quarter's file Last-Modified {f.last_modified}; "
            f"{f.requests:,} requests, {f.bytes:,} bytes",
            f"Run log: warehouse/output/logs/ferc_eqr_contracts_{run_id}.log",
            f"Raw files: warehouse/raw/{NAME}/{args.quarter}/ (not in git): each filing's contracts file as served, and index.json",
            f"Source: {SOURCE} Federal Energy Regulatory Commission, Electric Quarterly Reports, quarterly filings of all companies, "
            f"CSV_{args.quarter}.zip, {public_url(url)}",
            f"  page: {VIEWER}",
            "License: internal. Public filings published by FERC; its license statement could not be read by this machine (ferc.gov "
            "answers automated requests with HTTP 403), and session 83's instruction is an internal table.",
        ]
        if args.limit:
            trial = os.path.join(ip.ROOT, "runs", f"ferc_eqr_contracts_trial_{args.quarter}.csv")
            os.makedirs(os.path.dirname(trial), exist_ok=True)
            with open(trial, "w", encoding="utf-8", newline="") as out:
                for h in header:
                    out.write("# " + h + "\n")
                d.to_csv(out, index=False, lineterminator="\n")
            print(f"trial: {len(filings):,} filings, {len(d):,} rows -> {os.path.relpath(trial, ip.ROOT)}; no table written")
            log.close()
            return 0
        table = HISTORY if args.history else NAME
        if args.history:
            header[0] = ("Energy Research Warehouse (ERW): FERC Electric Quarterly Reports, the contracts as filed for the quarters before the newest "
                         f"(session 125's approved pull; this run wrote {args.quarter.replace('_', ' ')}; x_quarter says which quarter a row was filed for)")
            header.insert(1, f"The newest quarter is the table {NAME}. Every agreement in force is filed again each quarter: a contract is in this table once for each "
                             "quarter it was filed in, so its rows are never added up across quarters.")
        ip.write_csv(d, table, header, log, cols=COLS, key=["event_id"], time_col="event_date")
        documents = public_url(url)
        if args.history:  # the registry's row keeps naming the newest quarter's file; an earlier quarter adds its table only
            reg = os.path.join(ip.METADATA_DIR, "sources.csv")
            was = pd.read_csv(reg, dtype=str, keep_default_na=False) if os.path.exists(reg) else pd.DataFrame(columns=["source", "document_list"])
            kept = was.loc[was["source"] == SOURCE, "document_list"]
            documents = kept.iloc[0] if len(kept) else documents
        ip.update_sources([dict(source=SOURCE, publisher="Federal Energy Regulatory Commission (FERC)",
                                report="Electric Quarterly Reports (EQR): contracts, quarterly filings of all companies", report_url=VIEWER,
                                document_list=documents, license="internal", tables=[table])])
        results.append(dict(table=table, market="contracts", status="ok", detail=f"{len(d):,} rows, {counts['companies']:,} companies"))
        print(f"{table}: {len(d):,} rows, {counts['companies']:,} companies, {args.quarter}; {f.requests:,} requests, {f.bytes / 1e9:.2f} GB")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"{NAME} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="contracts", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    ip.write_status(NAME, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
