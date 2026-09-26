#!/usr/bin/env python3
"""Load the ERW live set into Supabase (session 10).

Energy Research Warehouse (ERW). Upserts only the live set that
warehouse/supabase/live_set.yaml defines. Rows go into the shape tables
series, entities and events (with table_name and license); coverage.csv goes
into catalogue and sources.csv into sources. The schema is
warehouse/supabase/migrations/, applied by warehouse/supabase/apply.py.

    python warehouse/supabase/load.py              # load, reconcile, check the size
    python warehouse/supabase/load.py --dry-run    # select and count only; no network

Writes with SUPABASE_URL and SUPABASE_SERVICE_KEY (the service role bypasses
row-level security; the key is never printed). For each table:
- the live-set rows are selected from the CSV (whole, or the last N days);
- they are upserted in batches, stamped with this run's loaded_at;
- the table's rows with an older loaded_at are deleted, so rows that left the
  source or the window leave Supabase too;
- count(*) in Supabase for that table_name must equal the selected CSV rows.
Then pg_database_size (function erw_db_size) must be under max_mb (300), or the
run fails. Exit 1 on any failure.
"""

import argparse
import datetime as dt
import json
import math
import os
import re
import sys
import urllib.parse

import pandas as pd
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "warehouse", "output")
LIVE = yaml.safe_load(open(os.path.join(HERE, "live_set.yaml"), encoding="utf-8"))
BATCH = 1000
TS_FMT = "%Y-%m-%dT%H:%M:%SZ"

SERIES_COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node",
               "source", "source_url", "retrieved_at", "vintage"]
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status",
               "status_date", "operator", "source", "source_url", "retrieved_at", "vintage"]
EVENT_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price",
              "currency", "status", "source", "source_url"]
SHAPES = {"series": (SERIES_COLS, ["table_name", "entity", "variable", "ts_utc"]),
          "entities": (ENTITY_COLS, ["table_name", "entity_id"]),
          "events": (EVENT_COLS, ["table_name", "event_id"])}
NUMERIC = {"value", "lat", "lon", "capacity_mw", "mw", "price"}
TIMESTAMP = {"ts_utc", "retrieved_at", "event_date"}
CAT_NUMERIC = {"n_nodes", "n_rows"}


def env(name):
    v = os.environ.get(name)
    if not v:
        from dotenv import dotenv_values
        v = dotenv_values(os.path.join(ROOT, ".env")).get(name)
    v = (v or "").strip()
    if not v:
        raise SystemExit(f"{name} is not set (.env or environment); nothing loaded")
    return v


def read_table(name):
    path = os.path.join(OUT, name + ".csv")
    with open(path, encoding="utf-8") as f:
        n = sum(1 for line in f if line.startswith("#"))
    return pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False, na_values=[])


def shape_of(df):
    cols = list(df.columns)
    if cols[:2] == ["entity_id", "entity_type"]:
        return "entities"
    if cols[:1] == ["event_id"]:
        return "events"
    return "series"


def select_live():
    """[(table, rule, days)] for every table in warehouse/output the live set includes."""
    names = sorted(os.path.splitext(f)[0] for f in os.listdir(OUT) if f.endswith(".csv"))
    out = []
    for n in names:
        if any(re.match(p, n) for p in LIVE["full"]):
            out.append((n, "full", None))
        elif any(re.match(p, n) for p in LIVE["recent"]["tables"]):
            out.append((n, "recent", LIVE["recent"]["days"]))
    return out


def filtered(name, days, now):
    df = read_table(name)
    shape = shape_of(df)
    if days is not None:
        if shape != "series":
            raise RuntimeError(f"{name}: a day window applies to series tables only")
        cut = (now - pd.Timedelta(days=days)).strftime(TS_FMT)
        df = df[df["ts_utc"] >= cut]  # ISO 8601 UTC strings sort as times
    return df, shape


def records(name, df, shape, license_, loaded_at):
    cols, _ = SHAPES[shape]
    extra_cols = [c for c in df.columns if c not in cols]
    out = []
    for row in df.to_dict("records"):
        r = {"table_name": name, "license": license_, "loaded_at": loaded_at}
        for c in cols:
            v = row.get(c, "")
            if v == "":
                r[c] = None
            elif c in NUMERIC:
                x = float(v)
                r[c] = None if math.isnan(x) else x
            else:
                r[c] = v
        if shape != "series":
            r["extra"] = {c: row[c] for c in extra_cols if row[c] != ""}
        out.append(r)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW Supabase live-set loader")
    ap.add_argument("--dry-run", action="store_true", help="select and count only, no network")
    args = ap.parse_args(argv)
    now = pd.Timestamp.now(tz="UTC")
    loaded_at = now.strftime(TS_FMT)
    cov = pd.read_csv(os.path.join(ROOT, LIVE["catalogue"]), dtype=str, keep_default_na=False)
    lic = dict(zip(cov["table"], cov["license"]))
    plan = select_live()
    print(f"live set: {len(plan)} tables ({sum(r == 'full' for _, r, _ in plan)} whole, "
          f"{sum(r == 'recent' for _, r, _ in plan)} last {LIVE['recent']['days']} days)")

    selected = {}
    for name, rule, days in plan:
        df, shape = filtered(name, days, now)
        selected[name] = (df, shape)
        print(f"  {name}: {shape}, {rule}, {len(df):,} rows, license {lic.get(name)}")
    total = sum(len(df) for df, _ in selected.values())
    print(f"rows selected: {total:,}")
    if args.dry_run:
        return 0

    from supabase import create_client
    u = urllib.parse.urlparse(env("SUPABASE_URL"))
    client = create_client(f"{u.scheme}://{u.netloc}", env("SUPABASE_SERVICE_KEY"))
    for t in ("series", "entities", "events", "catalogue", "sources", "headers"):
        try:
            client.table(t).select("*", count="exact", head=True).limit(1).execute()
        except Exception as exc:
            raise SystemExit(f"FAILED: Supabase table {t} is not reachable ({type(exc).__name__}: "
                             f"{str(exc)[:200]}). Apply the migrations first: warehouse/supabase/apply.py")

    failed = []
    recon = []
    for name, (df, shape) in selected.items():
        _, key = SHAPES[shape]
        try:
            if name not in lic:
                raise RuntimeError("not in coverage.csv")
            recs = records(name, df, shape, lic[name], loaded_at)
            for i in range(0, len(recs), BATCH):
                client.table(shape).upsert(recs[i:i + BATCH], on_conflict=",".join(key)).execute()
            client.table(shape).delete().eq("table_name", name).lt("loaded_at", loaded_at).execute()
            n = client.table(shape).select("table_name", count="exact", head=True) \
                .eq("table_name", name).execute().count
            ok = n == len(df)
            recon.append((name, shape, len(df), n, "match" if ok else "MISMATCH"))
            print(f"{'match   ' if ok else 'MISMATCH'} {name}: CSV (filtered) {len(df):,}, Supabase {n:,}")
            if not ok:
                failed.append(name)
        except Exception as exc:
            failed.append(name)
            recon.append((name, shape, len(df), None, f"FAILED {type(exc).__name__}"))
            print(f"FAILED {name}: {type(exc).__name__}: {str(exc)[:300]}")

    # provenance headers of every live-set table
    hdr = []
    for name in selected:
        path = os.path.join(OUT, name + ".csv")
        with open(path, encoding="utf-8") as f:
            lines = [ln.rstrip("
")[1:].strip() for ln in f if ln.startswith("#")]
        hdr += [{"table_name": name, "line_no": i, "line": ln, "license": lic[name]}
                for i, ln in enumerate(lines, 1)]
    client.table("headers").delete().neq("table_name", "").execute()
    for i in range(0, len(hdr), BATCH):
        client.table("headers").insert(hdr[i:i + BATCH]).execute()

    # catalogue (coverage.csv) and sources, loaded whole
    live_names = set(selected)
    cat = []
    for r in cov.to_dict("records"):
        row = {("table_name" if k == "table" else k): (None if v == "" else v) for k, v in r.items()}
        for k in CAT_NUMERIC:
            row[k] = None if row.get(k) is None else int(row[k])
        row["in_live_set"] = "yes" if r["table"] in live_names else "no"
        cat.append(row)
    client.table("catalogue").upsert(cat, on_conflict="table_name").execute()
    client.table("catalogue").delete().not_.in_("table_name", list(cov["table"])).execute()
    reg = pd.read_csv(os.path.join(ROOT, LIVE["sources"]), dtype=str, keep_default_na=False)
    srcs = [{k: (None if v == "" else v) for k, v in r.items()} for r in reg.to_dict("records")]
    for i in range(0, len(srcs), BATCH):
        client.table("sources").upsert(srcs[i:i + BATCH], on_conflict="source").execute()
    for t, want in (("catalogue", len(cat)), ("sources", len(srcs))):
        n = client.table(t).select("*", count="exact", head=True).execute().count
        ok = n == want
        recon.append((t, "meta", want, n, "match" if ok else "MISMATCH"))
        print(f"{'match   ' if ok else 'MISMATCH'} {t}: CSV {want:,}, Supabase {n:,}")
        if not ok:
            failed.append(t)

    size = client.rpc("erw_db_size").execute().data
    mb = int(size) / 1024 / 1024
    print(f"pg_database_size: {int(size):,} bytes ({mb:.1f} MB); limit {LIVE['max_mb']} MB")
    os.makedirs(os.path.join(ROOT, "runs"), exist_ok=True)
    pd.DataFrame(recon, columns=["table", "shape", "csv_rows", "supabase_rows", "result"]).to_csv(
        os.path.join(ROOT, "runs", "supabase_reconcile.csv"), index=False)
    with open(os.path.join(ROOT, "runs", "supabase_size.json"), "w", encoding="utf-8") as f:
        json.dump({"bytes": int(size), "mb": round(mb, 1), "at": loaded_at}, f)
    if mb > LIVE["max_mb"]:
        print(f"FAILED: database is {mb:.1f} MB, over the {LIVE['max_mb']} MB limit", file=sys.stderr)
        return 1
    if failed:
        print(f"FAILED tables: {failed}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
