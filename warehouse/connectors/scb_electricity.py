#!/usr/bin/env python3
"""Sweden's net electricity supply by type of production, a month from January 1974, as Statistics Sweden (SCB)
publishes the Swedish Energy Agency's statistics (table TAB1011): hydro, wind, nuclear, solar, conventional thermal and
its kinds, imports, and the sum (session 2236, chain 099: a third source of the session's own choosing).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/scb_sweden_electricity_monthly.csv, from
SCB's PxWebApi v2 (no key), two GETs:

    https://statistikdatabasen.scb.se/api/v2/tables/TAB1011/metadata?lang=en       the dimensions and their labels
    https://statistikdatabasen.scb.se/api/v2/tables/TAB1011/data?lang=en&...       every cell as JSON-stat 2.0

    entity      scb:se
    variable    the type of production in snake case, as SCB's English label gives it (sum_of_supply, hydro_power, wind,
                nuclear_power, solar_power, conventional_thermal_power, of_which_back_pressure_industrial,
                of_which_back_pressure_district_heating_work, of_which_condensation, of_which_gas_turbine_etc, import);
                node the label as SCB writes it; x_code SCB's code (Tot, Vatten, Vind, Karn, ...)
    unit        MWh (the table's GWh times 1,000); ts_utc the month's first day; freq P1M; geo SE

SCB's note: "import includes transit through Sweden from abroad. Loop force is excluded." Totals are SCB's lines, never
sums made here; a cell SCB leaves empty has no row; nothing is filled. A table whose dimensions are not the three
expected, a content not in GWh, a month not of the form YYYYMmm, a value array not the size of the dimensions or a line
and month given twice stops the run.

    python warehouse/connectors/scb_electricity.py [--offline] [--out-dir DIR]

Ceiling: two requests, saved in warehouse/raw/scb_electricity/ and reused offline (SCB allows ten calls in ten seconds and
100,000 values a table; this table has 6,952). statistikdatabasen.scb.se has no robots file (HTTP 404); www.scb.se's
allows all (session 2236). License: CC0 (SCB's open data page: "We use the licence CC0 for this data"); SCB asks that
statistics with another agency as their source state it: Swedish Energy Agency, via Statistics Sweden.
"""

import argparse
import datetime as dt
import itertools
import json
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "scb_sweden_electricity_monthly"
CONNECTOR = "scb_electricity"
SOURCE = "scb:TAB1011"
API = "https://statistikdatabasen.scb.se/api/v2/tables/TAB1011"
META = API + "/metadata?lang=en"
DATA = API + "/data?lang=en&valueCodes[Prodslag]=*&valueCodes[ContentsCode]=*&valueCodes[Tid]=*&outputFormat=json-stat2"
PAGE = "https://www.statistikdatabasen.scb.se/pxweb/en/ssd/START__EN__EN0108/"
TERMS = "https://www.scb.se/en/services/open-data-api/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
X_COLS = ["x_code"]


def slug(s):
    s = re.sub(r"\(.*?\)|,? net$", "", s.strip().lower()).strip()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


def parse(js, base):
    dims = js.get("id")
    if dims != ["Prodslag", "ContentsCode", "Tid"] and sorted(dims or []) != ["ContentsCode", "Prodslag", "Tid"]:
        raise RuntimeError(f"the table's dimensions are not the three expected: {dims}")
    size = js["size"]
    cats = []
    for d in dims:
        c = js["dimension"][d]["category"]
        idx = c["index"]
        codes = sorted(idx, key=idx.get) if isinstance(idx, dict) else list(idx)
        cats.append((d, codes, c.get("label", {})))
    content = js["dimension"]["ContentsCode"]["category"]["label"]
    if not all(v.strip() == "GWh" for v in content.values()):
        raise RuntimeError(f"a content not in GWh: {content}")
    values = js["value"]
    n = 1
    for s in size:
        n *= s
    if len(values) != n:
        raise RuntimeError(f"{len(values)} values for dimensions of size {size}")
    labels = next(c[2] for c in cats if c[0] == "Prodslag")
    rows = []
    for k, combo in enumerate(itertools.product(*[c[1] for c in cats])):
        v = values[k]
        if v is None:
            continue
        cell = dict(zip(dims, combo))
        m = re.fullmatch(r"(\d{4})M(\d\d)", cell["Tid"])
        if not m:
            raise RuntimeError(f"a month not of the form YYYYMmm: {cell['Tid']!r}")
        code = cell["Prodslag"]
        label = labels[code]
        rows.append(dict(entity="scb:se", variable=slug(label), ts_utc=f"{m.group(1)}-{m.group(2)}-01T00:00:00Z", value=round(float(v) * 1000, 3),
                         unit="MWh", freq="P1M", geo="SE", market="", node=label.strip(), **base, x_code=code))
    t = pd.DataFrame(rows)
    if t.empty:
        raise RuntimeError("no value in the answer")
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("a line and month given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="SCB TAB1011: Sweden's net electricity supply by type of production, a month")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if ip.paused(CONNECTOR) or ip.paused_host("statistikdatabasen.scb.se"):
        print(f"{NAME}: the publisher is paused (warehouse/metadata/paused_sources.csv); nothing asked")
        return 0
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
        meta, _ = ip.fetch_raw(CONNECTOR, META, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=60, pause=2)
        content, rec = ip.fetch_raw(CONNECTOR, DATA, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120, pause=2)
        m = json.loads(meta.decode("utf-8"))
        js = json.loads(content.decode("utf-8"))
        base = dict(source=SOURCE, source_url=API, retrieved_at=rec.get("retrieved_at") or "", vintage=js.get("updated", "") or m.get("updated", ""))
        t = parse(js, base)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "ts_utc"]).reset_index(drop=True)
        tot = t[t.variable == "sum_of_supply"].assign(y=lambda q: q.ts_utc.str[:4]).groupby("y").value.agg(["sum", "size"])
        tot = tot[tot["size"] == 12]["sum"] / 1e6
        note = " ".join(m.get("note") or js.get("note") or [])
        head = [
            "Energy Research Warehouse (ERW): Statistics Sweden (SCB), table TAB1011, Electricity supply in Sweden by type of production (the Swedish "
            f"Energy Agency's statistics), a month, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]} (session 2236)",
            "Shape: series (docs/datastandard.md v0). entity scb:se; variable the type of production in snake case (sum_of_supply, hydro_power, wind, "
            "nuclear_power, solar_power, conventional_thermal_power and its kinds, import); unit MWh (the table's GWh times 1,000); ts_utc the month's "
            "first day; freq P1M; geo SE; node SCB's label; x_code SCB's code.",
            f"{len(t)} rows, {t.variable.nunique()} lines; the sum of supply TWh a full year: " + ", ".join(f"{k} {v:.1f}" for k, v in tot.items() if k >= "2015")
            + f". SCB's note: {note} Totals are SCB's lines, never sums made here; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/scb_electricity.py; the data retrieved {base['retrieved_at']}; SCB's updated {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Swedish Energy Agency, via Statistics Sweden, table TAB1011, {PAGE}",
            f"  access: {META} ; {DATA}",
            f"License: public (CC0, {TERMS}). Source: Swedish Energy Agency, via Statistics Sweden.",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.variable.nunique()} lines, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Statistics Sweden (SCB)", report="Table TAB1011: Electricity supply in Sweden by type of production, monthly",
                                    report_url=PAGE, document_list=API, license="public", tables=[NAME])])  # CC0
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
