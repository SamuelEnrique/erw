#!/usr/bin/env python3
"""ERW, the deal tracker (/deals): the rows the replication reads (session 7404, chain 303).

It reads the live set (Supabase, the public read the site itself makes, with the anon key) and writes the rows the
pages are drawn from into this folder's rows/ (never in git with the replication: energy_deals is held, "license
needed", since 21 October 2026):

    rows/energy_deals.json    the table as the live set serves it (the select of site/lib/data.ts, deals)
    rows/deals_slim.csv       for the do-file: one line a deal, the fields the counts read, no free text but names
    rows/retrieved.json       when, from where, and how many rows

    python replication/deals/fetch_rows.py
    python replication/deals/fetch_rows.py --csv-only    # the do-file's CSV again from rows/energy_deals.json, no request

SUPABASE_URL and SUPABASE_ANON_KEY are read from the environment, else from the repository's .env. Standard library
only. Exit 0 when the read answered, 2 when it did not (nothing is written then: no partial file).
"""
import csv
import datetime
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ROWS = os.path.join(HERE, "rows")
PAGE = 1000
SELECT = "event_id,event_date,status,mw,price,currency,parties,source,source_url,extra"
SLIM = ["event_id", "date", "deal_type", "kind", "status", "mw", "usd_per_mwh", "dollars", "ai_power", "state", "technology", "confidence", "folded_duplicate"]


def env(name):
    """The variable from the environment, else from the .env of this checkout or of the main checkout beside it."""
    if os.environ.get(name):
        return os.environ[name]
    for folder in (ROOT, os.path.join(os.path.dirname(ROOT), "erw")):
        path = os.path.join(folder, ".env")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                for line in f:
                    if line.startswith(name + "="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit(f"{name} is not set (the environment or .env)")


def rest(table, query, limit=50000):
    """Every row of a read of the live set, a page of 1,000 at a time."""
    url, key = env("SUPABASE_URL").rstrip("/"), env("SUPABASE_ANON_KEY")
    if url.endswith("/rest/v1"):       # a .env may hold the project's address with or without the REST path
        url = url[: -len("/rest/v1")]
    out, offset = [], 0
    while offset < limit:
        qs = urllib.parse.urlencode({**query, "limit": str(PAGE), "offset": str(offset)})
        req = urllib.request.Request(f"{url}/rest/v1/{table}?{qs}", headers={"apikey": key, "Authorization": f"Bearer {key}"})
        with urllib.request.urlopen(req, timeout=60) as r:
            page = json.loads(r.read().decode("utf-8"))
        out.extend(page)
        if len(page) < PAGE:
            break
        offset += PAGE
    return out


def write_slim(stamp):
    """The do-file's CSV, from the JSON already in rows/: plain fields, so Stata reads it without quoting rules."""
    with open(os.path.join(ROWS, "energy_deals.json"), encoding="utf-8") as f:
        deals = json.load(f)
    plain = lambda v: "" if v is None else " ".join(str(v).replace(",", " ").replace('"', "").split())
    # the register's folded pairs, as the site holds them: the duplicate of a pair whose two rows are both held is marked,
    # so the do-file can count each such deal once, as the tracker does
    with open(os.path.join(ROOT, "site", "data", "deal_duplicates.json"), encoding="utf-8") as f:
        pairs = json.load(f)["pairs"]
    ids = {r["event_id"] for r in deals}
    folded = {p["duplicate"] for p in pairs if p["ruling"] == "fold" and p["duplicate"] in ids and p["kept"] in ids}
    with open(os.path.join(ROWS, "deals_slim.csv"), "w", encoding="utf-8", newline="") as f:
        f.write(f"# ERW replication, energy_deals as the live set served it at {stamp} (held: license needed; not for redistribution)" + chr(10))
        w = csv.writer(f, lineterminator=chr(10))
        w.writerow(SLIM)
        for r in deals:
            x = r.get("extra") or {}
            w.writerow([plain(v) for v in (r["event_id"], (r.get("event_date") or "")[:10], x.get("deal_type"), x.get("kind"), r.get("status"), r.get("mw"),
                                           r.get("price"), x.get("dollars"), str(x.get("ai_power") or "").lower(), (x.get("state") or "").upper(),
                                           x.get("technology"), x.get("confidence"), 1 if r["event_id"] in folded else 0)])
    return len(deals)


def main():
    if "--csv-only" in sys.argv:
        with open(os.path.join(ROWS, "retrieved.json"), encoding="utf-8") as f:
            stamp = json.load(f)["retrieved_at"]
        print(f"written from rows/energy_deals.json of {stamp}: deals_slim.csv ({write_slim(stamp)} rows)")
        return 0
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        deals = rest("events", {"select": SELECT, "table_name": "eq.energy_deals", "order": "event_date.desc,event_id"})
    except (urllib.error.URLError, OSError, ValueError) as exc:
        print(f"the read of the live set failed, nothing written: {exc}")
        return 2
    os.makedirs(ROWS, exist_ok=True)
    with open(os.path.join(ROWS, "energy_deals.json"), "w", encoding="utf-8") as f:
        json.dump(deals, f, ensure_ascii=True, indent=0)
    with open(os.path.join(ROWS, "retrieved.json"), "w", encoding="utf-8") as f:
        json.dump({"retrieved_at": now, "source": "the ERW live set (Supabase), a public read with the anon key", "energy_deals": len(deals),
                   "newest_deal": max((r.get("event_date") or "")[:10] for r in deals) if deals else ""}, f, indent=0)
    write_slim(now)
    print(f"{now}: energy_deals {len(deals)} rows, written to {ROWS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
