#!/usr/bin/env python3
"""ERW, the project map (/map, the Projects tab): the rows the replication reads (session 7601, chain 305).

Three reads, each of a public source, into this folder's rows/ (never in git):

    rows/eia860m.xlsx                EIA's own workbook of the month the page's file names (Form EIA-860M, public domain),
                                     from the address the page's file carries (source_url), as EIA serves it
    rows/units.csv                   its four sheets (Operating, Operating_PR, Planned, Planned_PR), one line a generating
                                     unit, the columns the map reads and the net summer capacity the cross-check reads, each as the workbook gives it
    rows/queue.json                  the queue positions of energy_projects, every status, from the ERW live set
                                     (Supabase, the public reads the site itself makes, with the anon key)
    rows/datacenter_facilities.json  the facilities of the datacenter tracker, from the live set. The table is held
                                     ("license needed"): its rows are not published by this repository's replication
    rows/retrieved.json              when, from where, and how many rows of each

    python replication/map/fetch_rows.py                # all three
    python replication/map/fetch_rows.py --units-only    # the workbook alone (no key needed)
    python replication/map/fetch_rows.py --csv-only      # units.csv again from the workbook already here, no request

EIA's robots file allows /electricity/ (read 16 November 2026). The workbook is read with openpyxl (requirements.txt);
everything else is the standard library. SUPABASE_URL and SUPABASE_ANON_KEY are read from the environment, else from
the repository's .env. Exit 0 when every read answered, 2 when one did not.
"""
import csv
import datetime
import json
import os
import sys
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ROWS = os.path.join(HERE, "rows")
PAGE_FILE = os.path.join(ROOT, "site", "data", "map.json")
AGENT = "erw-replication (python)"
SHEETS = [("Operating", "operating"), ("Operating_PR", "operating"), ("Planned", "planned"), ("Planned_PR", "planned")]
# the workbook's own column names (its third line), and the short names units.csv gives them
COLUMNS = [("Plant ID", "plant_id"), ("Generator ID", "generator_id"), ("Plant Name", "plant_name"), ("Plant State", "plant_state"),
           ("Nameplate Capacity (MW)", "nameplate_mw"), ("Technology", "technology"), ("Prime Mover Code", "prime_mover"), ("Status", "status"),
           ("Balancing Authority Code", "balancing_authority"), ("Latitude", "latitude"), ("Longitude", "longitude"),
           ("Net Summer Capacity (MW)", "net_summer_mw")]
ENTITY_SELECT = "entity_id,name,geo,lat,lon,capacity_mw,status,operator,vintage,retrieved_at,extra"
PAGE = 1000


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
                        return line.split("=", 1)[1].strip().strip('"')
    return ""


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def workbook_url():
    with open(PAGE_FILE, encoding="utf-8") as f:
        return json.load(f)["source_url"]


def fetch_workbook(url):
    req = urllib.request.Request(url, headers={"User-Agent": AGENT})
    with urllib.request.urlopen(req, timeout=300) as r:
        body = r.read()
        stamp = r.headers.get("Last-Modified", "")
    if len(body) < 1_000_000 or body[:2] != b"PK":
        raise RuntimeError(f"{url} did not answer with a workbook ({len(body)} bytes)")
    with open(os.path.join(ROWS, "eia860m.xlsx"), "wb") as f:
        f.write(body)
    return len(body), stamp


def units_csv():
    """units.csv from the workbook: each sheet's title is on line 1, its column names on line 3, a unit a line after."""
    import openpyxl
    wb = openpyxl.load_workbook(os.path.join(ROWS, "eia860m.xlsx"), read_only=True, data_only=True)
    out, counts, titles = [], {}, {}
    for sheet, kind in SHEETS:
        ws = wb[sheet]
        rows = ws.iter_rows(values_only=True)
        titles[sheet] = str(next(rows)[0] or "").strip()
        next(rows)
        head = [str(c).strip() if c is not None else "" for c in next(rows)]
        at = {name: head.index(name) for name, _ in COLUMNS}
        month = ("Operating Month", "Operating Year") if kind == "operating" else ("Planned Operation Month", "Planned Operation Year")
        at_m, at_y = head.index(month[0]), head.index(month[1])
        n = 0
        for r in rows:
            if r[at["Plant ID"]] is None or r[at["Generator ID"]] is None or not str(r[at["Plant ID"]]).strip().isdigit():
                continue                                   # the notes under a sheet's last unit
            cells = ["" if r[at[name]] is None else str(r[at[name]]).strip() for name, _ in COLUMNS]
            out.append([sheet, kind] + cells + ["" if r[at_y] is None else str(r[at_y]).strip(), "" if r[at_m] is None else str(r[at_m]).strip()])
            n += 1
        counts[sheet] = n
    wb.close()
    with open(os.path.join(ROWS, "units.csv"), "w", encoding="utf-8", newline="") as f:
        f.write(f"# ERW replication of /map: the generating units of EIA's Form EIA-860M workbook, four sheets, each cell as the workbook gives it. Written {now()}.\n")
        w = csv.writer(f)
        w.writerow(["sheet", "kind"] + [short for _, short in COLUMNS] + ["year", "month"])
        w.writerows(out)
    return counts, titles


def rest(path):
    base = env("SUPABASE_URL").split("/rest/v1")[0].rstrip("/")
    key = env("SUPABASE_ANON_KEY")
    if not base or not key:
        raise RuntimeError("SUPABASE_URL or SUPABASE_ANON_KEY is not set")
    req = urllib.request.Request(base + "/rest/v1/" + path, headers={"apikey": key, "Authorization": "Bearer " + key, "User-Agent": AGENT})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def entities(filters):
    out, start = [], 0
    while True:
        q = urllib.parse.urlencode({"select": ENTITY_SELECT, **filters, "order": "entity_id.asc", "limit": PAGE, "offset": start}, safe=",.>*()-")
        page = rest("entities?" + q)
        out.extend(page)
        if len(page) < PAGE:
            return out
        start += PAGE


def main(argv):
    os.makedirs(ROWS, exist_ok=True)
    got = {"written": now()}
    try:
        if "--csv-only" not in argv:
            url = workbook_url()
            size, stamp = fetch_workbook(url)
            got["workbook"] = {"url": url, "bytes": size, "last_modified": stamp, "retrieved": now()}
        counts, titles = units_csv()
        got["units"] = {"rows": sum(counts.values()), "by_sheet": counts, "titles": titles}
        if "--units-only" not in argv and "--csv-only" not in argv:
            queue = entities({"table_name": "eq.energy_projects", "extra->>kind": "eq.queue"})
            dc = entities({"table_name": "eq.datacenter_facilities"})
            for name, rows in (("queue", queue), ("datacenter_facilities", dc)):
                with open(os.path.join(ROWS, name + ".json"), "w", encoding="utf-8") as f:
                    json.dump(rows, f, ensure_ascii=False)
                got[name] = {"rows": len(rows), "vintage": max((r.get("vintage") or "" for r in rows), default=""), "retrieved": now(),
                             "source": "the ERW live set (Supabase), public reads with the anon key"}
    except Exception as e:  # noqa: BLE001: any read that does not answer ends the run, loudly
        print(f"not read: {type(e).__name__}: {e}", file=sys.stderr)
        return 2
    path = os.path.join(ROWS, "retrieved.json")
    old = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            old = json.load(f)
    old.update(got)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(old, f, indent=1)
    print(json.dumps(got, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
