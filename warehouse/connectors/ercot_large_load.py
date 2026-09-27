#!/usr/bin/env python3
"""ERCOT large-load interconnection requests: a watch on ERCOT's Large Load Integration page.

Energy Research Warehouse (ERW) connector, session 17.

    python warehouse/connectors/ercot_large_load.py

The session 17 prompt asked for ERCOT's large-load interconnection status report as an
entities table, one row per request with MW, county, status and dates. As of 2026-09-27
ERCOT publishes no such list:
- Nodal Protocol 3.2.7 (NPRR1267, approved 2025-07-31) requires a monthly Large Load
  Interconnection Status Report that AGGREGATES requests (by location, load zone, TSP,
  load type, request date, energization date and size range, with at least three
  customers per category), because customer data is confidential;
- what ERCOT posts is the "Large Load Interconnection Status Update" slide deck (for example
  https://www.ercot.com/files/docs/2026/03/12/March-TAC-Report.pdf), whose numbers are
  chart images, and totals in the prose of some issues of "ERCOT Monthly";
- the Large Load Integration page (PAGE below) links forms, attestations and FAQs, not a
  request list.

So this connector does not invent rows. Each run it reads PAGE (saved under
warehouse/raw/ercot_large_load/<run_id>/), and looks for a spreadsheet link whose title or
file name names a status report or queue. If there is none, it fails loudly with that
reason and writes nothing. If ERCOT posts one, it is downloaded (raw) and read: a sheet
with a county column and a MW column becomes ercot_large_load_queue (entities, one row per
request, ERCOT's own status in ercot_status and a harmonized status); a file without
those columns fails with the columns it has, so the parser can be written against it.
Weekly: run_daily.sh runs it with the ISO queues (Mondays UTC, or QUEUES=1).
"""

import datetime as dt
import io
import os
import re
import sys
import traceback
from urllib.parse import urljoin

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "ercot_large_load_queue"
PAGE = "https://www.ercot.com/services/rq/large-load-integration"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
WANT = re.compile(r"(?i)(status report|interconnection status|large load queue|lli queue|interconnection queue)")
NOT = re.compile(r"(?i)(form|attestation|faq|guide|exhibit|question)")
STD = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date",
       "operator", "source", "source_url", "retrieved_at", "vintage"]
# ERCOT's status words (Large Load Interconnection Status Update, March 2026) -> entities vocabulary
STATUS = [(r"observed energized|operational", "operating"),
          (r"approv\w* to energize", "under_construction"),
          (r"planning studies approved|requirements met|approved", "planned"),
          (r"under ercot review|no studies submitted|review|submitted", "active"),
          (r"cancel|withdraw", "withdrawn")]


def links(html):
    """[(url, title)] of every spreadsheet linked from the page."""
    out = []
    for m in re.finditer(r'<a\s[^>]*href="([^"]+)"([^>]*)>([^<]*)', html, re.I):
        href, attrs, text = m.groups()
        if not re.search(r"\.(xlsx|xls|csv)(\?|$)", href, re.I):
            continue
        t = re.search(r'title="([^"]*)"', attrs)
        out.append((urljoin(PAGE, href), " ".join(((t.group(1) if t else "") or text).split())))
    return out


def col(df, pattern):
    hits = [c for c in df.columns if re.search(pattern, str(c), re.I)]
    return hits[0] if hits else None


def harmonize(s):
    s = str(s).lower()
    for pat, std in STATUS:
        if re.search(pat, s):
            return std
    return ""


def build(df, url, got):
    county, mw = col(df, r"county"), col(df, r"\bmw\b|megawatt|size")
    if county is None or mw is None:
        raise ip.SourceGap(f"{url}: no county or MW column; columns are {list(df.columns)[:20]}; "
                           "write the parser against this file")
    status, name = col(df, r"status"), col(df, r"project|name|id")
    t = pd.DataFrame({
        "entity_id": [f"ercot_large_load:{i + 1}" for i in range(len(df))],
        "entity_type": "project",
        "name": df[name].astype(str) if name else "",
        "geo": "US-TX", "lat": "", "lon": "",
        "capacity_mw": pd.to_numeric(df[mw], errors="coerce").map(lambda v: "" if pd.isna(v) else f"{v:g}"),
        "status": df[status].map(harmonize) if status else "",
        "status_date": "", "operator": "", "source": "ercot:large_load_queue", "source_url": url,
        "retrieved_at": got, "vintage": got[:10],
        "county": df[county].astype(str).str.strip(), "state": "TX",
        "ercot_status": df[status].astype(str) if status else "",
    })
    for c in [c for c in df.columns if re.search(r"date", str(c), re.I)]:
        t[re.sub(r"[^a-z0-9]+", "_", str(c).lower()).strip("_")] = pd.to_datetime(
            df[c], errors="coerce").dt.strftime("%Y-%m-%d").fillna("")
    return t


def main():
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"ercot_large_load_{run_id}.log"))
    ip.RAW.open("ercot_large_load", run_id)
    status = dict(table=NAME, market="large_load", status="ok", detail="")
    try:
        r = ip.with_retries("ERCOT Large Load Integration page",
                            lambda: requests.get(PAGE, headers=UA, timeout=60), log, attempts=3, wait=5)
        if r.status_code != 200:
            raise RuntimeError(f"{PAGE}: HTTP {r.status_code}")
        sheets = links(r.text)
        log(f"{PAGE}: {len(sheets)} spreadsheet links: " + "; ".join(t or u for u, t in sheets))
        cands = [(u, t) for u, t in sheets if WANT.search(t + " " + u) and not NOT.search(t + " " + u)]
        if not cands:
            raise ip.SourceGap(
                f"ERCOT publishes no request-level large-load list: {PAGE} links {len(sheets)} spreadsheets, "
                "none a status report or queue (forms, FAQs, exhibits). Protocol 3.2.7 (NPRR1267) requires "
                "the monthly status report to aggregate requests; its numbers are chart images. No table written.")
        url, title = cands[0]
        log(f"candidate: {title} {url}")
        f = ip.with_retries("large-load file", lambda: requests.get(url, headers=UA, timeout=120), log,
                            attempts=3, wait=5)
        if f.status_code != 200:
            raise RuntimeError(f"{url}: HTTP {f.status_code}")
        got = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        df = pd.read_csv(io.BytesIO(f.content)) if url.lower().endswith(".csv") else pd.read_excel(io.BytesIO(f.content))
        t = build(df, url, got)
        ip.write_snapshot(t, NAME, [
            "Energy Research Warehouse (ERW): ERCOT large-load interconnection requests",
            "Shape: entities (docs/datastandard.md), a snapshot of ERCOT's file; status harmonized from "
            "ercot_status by warehouse/connectors/ercot_large_load.py (STATUS).",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/ercot_large_load.py",
            f"Source: ercot:large_load_queue {title}, {url}; found on {PAGE}",
            f"Raw files: warehouse/raw/ercot_large_load/{run_id}/",
            "License: public (an ERCOT public report).",
        ], log, list(t.columns))
        ip.update_sources([dict(source="ercot:large_load_queue", publisher=ip.ISO_PUBLISHERS["ercot"],
                                report=title, report_url=url, document_list=PAGE, license="public",
                                tables=[NAME])])
        status["detail"] = f"{len(t)} requests from {url}"
    except Exception:
        tb = ip.redact(traceback.format_exc())
        last = tb.strip().splitlines()[-1]
        log(f"FAILED, no output file written:\n{tb}")
        print(f"ercot_large_load {NAME} FAILED, no output file written: {last}", file=sys.stderr)
        status.update(status="failed", detail=last[:300])
    ip.write_status("ercot_large_load", run_id, [status])
    log.close()
    print(f"ercot_large_load run log: {os.path.relpath(log.path, ip.ROOT)}")
    return 1 if status["status"] == "failed" else 0


if __name__ == "__main__":
    sys.exit(main())
