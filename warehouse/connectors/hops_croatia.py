#!/usr/bin/env python3
"""HOPS (Croatia's transmission system operator): the transmission network's yearly energy data, from its
"Elektroenergetski podaci" page: production by source, cross-border exchange, the energy carried, the system's peak and
minimum load, consumption, losses and deliveries to customers on the network, 2017 onwards (session 2823, chain 144).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/hops_croatia_annual.csv, from one page (one
request), whose one table the connector reads:

    https://www.hops.hr/elektroenergetski-podaci

    entity      hops:hr, or hops:hr:<source> for production (hydro, thermal, wind, solar)
    variable    generation (the transmission network's production, by source and total), imports (into Croatia, half of the
                Krsko nuclear plant's output included), exports, net_imports, energy_carried (the energy carried on the
                transmission network), peak_load and minimum_load (MW: the page's MWh/h, the hour's mean), consumption (on
                the transmission network, losses not included), losses, direct_customer_delivery (to customers connected to
                the transmission network)
    unit        MWh (the page's GWh times 1,000), or MW for the two loads
    ts_utc      the year's 1 January at 00:00:00Z; freq P1Y; geo HR
    node        "HOPS transmission network, <the page's row>"
    x_*         the page's row label (in Croatian), and for the two loads the day and hour it gives (local, as printed)

The page prints its numbers with a dot for thousands ("4.809" GWh is 4,809 GWh). Compared every year, within 1 GWh: the sources
against their total; imports less exports against the net; production plus imports against the energy carried; consumption,
losses and exports against the energy carried. A case that does not hold is counted in the header and listed in the run log,
kept as published; nothing is filled. Checks that stop the run: no table, a header not of years, a row not in the expected
structure, a value not a number.

    python warehouse/connectors/hops_croatia.py [--offline] [--out-dir DIR]

Ceiling: one request, reused from warehouse/raw/hops_croatia/ with --offline. www.hops.hr and hops.hr have no robots file
(HTTP 404, reads 1641 and 1642). License: internal until HOPS's terms are read (the page links none; its home page calls its
live figures informative only).
"""

import argparse
import datetime as dt
import html
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "hops_croatia_annual"
CONNECTOR = "hops_croatia"
SOURCE = "hops:elektroenergetski_podaci"
URL = "https://www.hops.hr/elektroenergetski-podaci"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
# (the page's first cell, its second cell): (entity suffix, variable, unit, factor)
ROWS = {("Proizvodnja na prijenosnoj mreži (GWh)", "Hidroelektrane"): ("hydro", "generation", "MWh", 1000.0),
        ("", "Termoelektrane"): ("thermal", "generation", "MWh", 1000.0),
        ("", "Vjetroelektrane"): ("wind", "generation", "MWh", 1000.0),
        ("", "Solarne elektrane"): ("solar", "generation", "MWh", 1000.0),
        ("", "Ukupna proizvodnja"): ("", "generation", "MWh", 1000.0),
        ("Prekogranična razmjena (GWh)", "Ulaz u RH (uključujući 50% NE Krško)"): ("", "imports", "MWh", 1000.0),
        ("", "Izlaz iz RH"): ("", "exports", "MWh", 1000.0),
        ("", "Razlika razmjene"): ("", "net_imports", "MWh", 1000.0),
        ("Ukupna prenesena energija na prijenosnoj mreži (GWh)", ""): ("", "energy_carried", "MWh", 1000.0),
        ("Najveće opterećenje sustava", "MWh/h"): ("", "peak_load", "MW", 1.0),
        ("Najmanje opterećenje sustava", "MWh/h"): ("", "minimum_load", "MW", 1.0),
        ("Potrošnja na prijenosnoj mreži bez gubitaka (GWh)", ""): ("", "consumption", "MWh", 1000.0),
        ("Gubici u prijenosnoj mreži (GWh)", ""): ("", "losses", "MWh", 1000.0),
        ("Isporuka svim kupcima izravno priključenim na prijenosnu mrežu (GWh)", ""): ("", "direct_customer_delivery", "MWh", 1000.0)}
TOL = 1.0   # GWh
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_label", "x_day", "x_hour"]


def cells(tr):
    return [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", c))).strip()
            for c in re.findall(r"(?s)<t[hd][^>]*>(.*?)</t[hd]>", tr)]


def number(s, where):
    v = s.replace(".", "").replace(" ", "")
    if not re.fullmatch(r"-?\d+", v):
        raise RuntimeError(f"{where}: not a number: {s!r}")
    return float(v)


def parse(content):
    s = content.decode("utf-8")
    tabs = re.findall(r"(?s)<table.*?</table>", s)
    if not tabs:
        raise RuntimeError("no table on the page")
    trs = [cells(tr) for tr in re.findall(r"(?s)<tr.*?</tr>", tabs[0])]
    head = trs[0]
    years = [re.fullmatch(r"(\d{4})\.?", h) for h in head[1:]]
    if head[0] != "Osnovni podaci" or not years or not all(years):
        raise RuntimeError(f"the header is not of years: {head}")
    years = [int(y.group(1)) for y in years]
    out, extra, last = [], {}, None
    for c in trs[1:]:
        if c[0] in ("Datum", "Sat") and last in ("peak_load", "minimum_load"):
            vals = c[1:]
        else:
            # a row with one label cell less than its numbers continues the block above
            if len(c) == len(years) + 2:
                key, vals = (c[0], c[1]), c[2:]
            elif len(c) == len(years) + 1:
                key, vals = (c[0], ""), c[1:]
                if key not in ROWS:
                    key = ("", c[0])
            else:
                raise RuntimeError(f"a row not in the expected structure: {c}")
            if key not in ROWS:
                raise RuntimeError(f"a row not in the expected structure: {c}")
            last = ROWS[key][1] if ROWS[key][1] in ("peak_load", "minimum_load") else None
        if len(vals) != len(years):
            raise RuntimeError(f"a row without a value for each year: {c}")
        if c[0] in ("Datum", "Sat") and last:
            for y, v in zip(years, vals):
                extra.setdefault((last, y), {})["x_day" if c[0] == "Datum" else "x_hour"] = v
            continue
        suffix, var, unit, k = ROWS[key]
        label = " / ".join(x for x in key if x)
        for y, v in zip(years, vals):
            out.append((suffix, var, unit, y, number(v, f"{label} {y}") * k, label))
    return years, out, extra


def frame(out, extra, retrieved, vintage):
    rows = []
    for suffix, var, unit, y, value, label in out:
        e = extra.get((var, y), {})
        rows.append({"entity": "hops:hr" + (f":{suffix}" if suffix else ""), "variable": var, "ts_utc": f"{y}-01-01T00:00:00Z",
                     "value": value, "unit": unit, "freq": "P1Y", "geo": "HR", "market": "",
                     "node": f"HOPS transmission network, {var.replace('_', ' ')}" + (f", {suffix}" if suffix else ""),
                     "source": SOURCE, "source_url": URL, "retrieved_at": retrieved, "vintage": vintage, "x_label": label,
                     "x_day": e.get("x_day", ""), "x_hour": e.get("x_hour", "")})
    t = pd.DataFrame(rows, columns=COLS)
    twice = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a key given twice: {twice.entity.iloc[0]} {twice.variable.iloc[0]} {twice.ts_utc.iloc[0]}")
    return t.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)


def checks(t):
    v = {(e, var, ts[:4]): x / 1000.0 for e, var, ts, x, u in zip(t.entity, t.variable, t.ts_utc, t.value, t.unit) if u == "MWh"}
    years = sorted({k[2] for k in v})
    off = []
    for y in years:
        g = lambda e, var: v.get((e, var, y))  # noqa: E731
        tests = {"sources against the total": (sum(g(f"hops:hr:{s}", "generation") or 0 for s in ("hydro", "thermal", "wind", "solar")), g("hops:hr", "generation")),
                 "imports less exports against the net": ((g("hops:hr", "imports") or 0) - (g("hops:hr", "exports") or 0), g("hops:hr", "net_imports")),
                 "production and imports against the energy carried": ((g("hops:hr", "generation") or 0) + (g("hops:hr", "imports") or 0), g("hops:hr", "energy_carried")),
                 "consumption, losses and exports against the energy carried": ((g("hops:hr", "consumption") or 0) + (g("hops:hr", "losses") or 0) + (g("hops:hr", "exports") or 0), g("hops:hr", "energy_carried"))}
        for name, (a, b) in tests.items():
            if b is not None and abs(a - b) > TOL:
                off.append((y, name, round(a - b, 3)))
    return 4 * len(years), off


def main(argv=None):
    ap = argparse.ArgumentParser(description="HOPS: Croatia's transmission network, its yearly energy data")
    ap.add_argument("--offline", action="store_true", help="the saved page only, no request")
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
        if not args.offline and (ip.paused("hops") or ip.paused_host("www.hops.hr")):
            raise RuntimeError("HOPS is paused (warehouse/metadata/paused_sources.csv): not requested")
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120)
        years, out, extra = parse(content)
        t = frame(out, extra, rec.get("retrieved_at") or "", ip.vintage_of(rec))
        n, off = checks(t)
        for x in off:
            log(f"  not as expected, kept as published: {x}")
        header = [
            f"Energy Research Warehouse (ERW): HOPS, Elektroenergetski podaci: Croatia's transmission network a year, production by source, cross-border exchange, the energy carried, peak and minimum load, consumption, losses and deliveries, {years[0]} to {years[-1]} (session 2823)",
            "Shape: series (docs/datastandard.md v0). entity hops:hr or hops:hr:<source> (hydro, thermal, wind, solar); variable generation, imports (half of Krsko's output included), exports, net_imports, energy_carried, peak_load, minimum_load, consumption (losses not included), losses, direct_customer_delivery; "
            "unit MWh (the page's GWh times 1,000), or MW for the two loads (the page's MWh/h); ts_utc the year's 1 January; freq P1Y; geo HR; x_label the page's row, x_day and x_hour the loads' day and hour as printed.",
            f"{len(t)} rows, {len(years)} years. The page's balances within {TOL:g} GWh: {n - len(off)} of {n} hold, the others kept as published and listed in the run log. A dot is the page's thousands separator. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/hops_croatia.py; the page retrieved {rec.get('retrieved_at') or ''}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} HOPS (Hrvatski operator prijenosnog sustava), Elektroenergetski podaci, {URL}",
            "License: see the ERW's license record (docs/licenses.md) for HOPS's terms. Source: HOPS; reshaped by the ERW.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="HOPS (the Croatian transmission system operator)",
                                    report="Elektroenergetski podaci (the transmission network's yearly energy data)",
                                    report_url=URL, document_list=URL, license="internal", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {years[0]} to {years[-1]}; balances {n - len(off)} of {n}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"{CONNECTOR} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
