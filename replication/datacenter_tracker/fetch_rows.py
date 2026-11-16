#!/usr/bin/env python3
"""ERW, the datacenter tracker (/datacenters): the rows the replication reads (session 7400, chain 303).

It reads the live set (Supabase, the public reads the site itself makes, with the anon key) and writes the rows the
page is drawn from into this folder's rows/ (never in git: datacenter_facilities is held, "license needed", and a row
of it is not published by this repository's replication either):

    rows/datacenter_facilities.json   the table as the live set serves it (the select of site/lib/data.ts, datacenters)
    rows/datacenter_facilities.csv    the same rows, one column a field (the extra keys as x_<key>), for the do-file
    rows/ercot_large_load_status.json the series rows of ERCOT's large-load status
    rows/queue_sites.json             the queue positions whose name or fuel field names a datacenter or a large load,
                                      of the queues that are not held (ERCOT's, CAISO's and SPP's on 16 November 2026)
    rows/queue_active.json            the active positions of the grids that hold such a site
    rows/retrieved.json               when, from where, and how many rows of each

    python replication/datacenter_tracker/fetch_rows.py

SUPABASE_URL and SUPABASE_ANON_KEY are read from the environment, else from the repository's .env. Standard library
only. Exit 0 when every read answered, 2 when one did not (nothing is written then: no partial file).
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
ENTITY_SELECT = "entity_id,entity_type,name,lat,lon,capacity_mw,status,status_date,operator,source,source_url,vintage,table_name,extra"
# site/lib/datacenter/bygrid.ts, QUEUE_SITE_PATTERN and QUEUE_GRIDS; the queues held on 16 November 2026 are not read
QUEUE_SITE_PATTERN = "data ?cent(?:er|re)s?|datacenter|large load|co-?located load|digital campus|hyperscale|crypto|bitcoin"
QUEUE_GRIDS = ["ercot", "caiso", "nyiso", "miso", "spp", "isone"]


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


def held_tables():
    """The tables held whole ("license needed") in warehouse/metadata/license_status.csv."""
    path = os.path.join(ROOT, "warehouse", "metadata", "license_status.csv")
    with open(path, encoding="utf-8", newline="") as f:
        return {r["table"] for r in csv.DictReader(f) if r["status"] == "license needed"}


def flat(rows):
    """One column a field: the standard columns, then every extra key as x_<key>, sorted."""
    keys = sorted({k for r in rows for k in (r.get("extra") or {})})
    head = [c for c in ENTITY_SELECT.split(",") if c != "extra"] + [f"x_{k}" for k in keys]
    body = []
    for r in rows:
        x = r.get("extra") or {}
        body.append([("" if r.get(c) is None else r.get(c)) for c in head[: len(head) - len(keys)]] + [x.get(k, "") or "" for k in keys])
    return head, body


def main():
    held = held_tables()
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        fac = rest("entities", {"select": ENTITY_SELECT, "table_name": "eq.datacenter_facilities", "order": "entity_id"})
        load = rest("series", {"select": "entity,variable,ts_utc,value,unit,table_name", "table_name": "eq.ercot_large_load_status", "order": "ts_utc,variable"})
        sites, read_grids, held_grids = {}, [], []
        for grid in QUEUE_GRIDS:
            table = f"{grid}_interconnection_queue"
            if table in held:
                held_grids.append(grid)
                continue
            read_grids.append(grid)
            for field in ("name", "extra->>fuel_technology"):
                for r in rest("entities", {"select": ENTITY_SELECT, "table_name": f"eq.{table}", field: f"imatch.{QUEUE_SITE_PATTERN}", "order": "entity_id"}, 2000):
                    sites[r["entity_id"]] = r
        site_rows = [sites[k] for k in sorted(sites)]
        grids = sorted({r["table_name"].replace("_interconnection_queue", "") for r in site_rows})
        active = []
        for grid in grids:
            active.extend(rest("entities", {"select": "table_name,capacity_mw,status,zone:extra->>zone", "table_name": f"eq.{grid}_interconnection_queue", "status": "eq.active", "order": "entity_id"}, 20000))
    except (urllib.error.URLError, OSError, ValueError) as exc:
        print(f"a read of the live set failed, nothing written: {exc}")
        return 2
    os.makedirs(ROWS, exist_ok=True)
    def dump(name, obj):
        with open(os.path.join(ROWS, name), "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=True, indent=0)
    dump("datacenter_facilities.json", fac)
    dump("ercot_large_load_status.json", load)
    dump("queue_sites.json", site_rows)
    dump("queue_active.json", active)
    head, body = flat(fac)
    with open(os.path.join(ROWS, "datacenter_facilities.csv"), "w", encoding="utf-8", newline="") as f:
        f.write(f"# ERW replication, datacenter_facilities as the live set served it at {now} (held: license needed; not for redistribution)\n")
        w = csv.writer(f)
        w.writerow(head)
        w.writerows(body)
    dump("retrieved.json", {"retrieved_at": now, "source": "the ERW live set (Supabase), public reads with the anon key",
                            "datacenter_facilities": len(fac), "ercot_large_load_status": len(load), "queue_sites": len(site_rows),
                            "queue_active": len(active), "queues_read": read_grids, "queues_held": held_grids,
                            "vintage": max((r.get("vintage") or "" for r in fac), default="")})
    print(f"{now}: datacenter_facilities {len(fac)} rows; ercot_large_load_status {len(load)}; queue sites {len(site_rows)} "
          f"(read: {', '.join(read_grids)}; held, not read: {', '.join(held_grids)}); active positions {len(active)}; written to {ROWS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
