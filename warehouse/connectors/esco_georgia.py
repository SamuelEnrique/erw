#!/usr/bin/env python3
"""Georgia's electricity balance a month, from the Electricity Market Operator's (ESCO) published actual balances:
generation by kind of plant, imports, transit, losses, supply to consumers by kind and exports, January 2021 to the
latest month published (session 2423, chain 115: in place of Cambodia, whose regulator's robots file disallows every
path).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/esco_georgia_electricity_monthly.csv, from
the two HTML tables (supply and consumption, million kWh) of each year's page of esco.ge's "Actual Balance", one request
a year (six when written; the current and the previous year's pages fetched again on a run, the others reused):

    https://esco.ge/en/energy-balance/by-year-1/<the year's page, as YEARS names it>

    entity     esco_ge:GE; geo GE; node Georgia; freq P1M; ts_utc the month's 1st; unit MWh (ESCO's million kWh times 1,000)
    variable   supply side: generation, generation_thermal, generation_wind, generation_solar, generation_hydro,
               generation_hydro_regulating, generation_hydro_seasonal, generation_hydro_small (ESCO's regulating,
               seasonal and small hydro plants), imports, transit_in, total_resource, plant_losses_self_consumption,
               delivery_to_network
               consumption side: supplied_to_consumers, supplied_distribution (the distribution companies),
               supplied_direct_customers, self_consumption_stopped_plants, exports, transit_out, supplied_and_export,
               network_losses (ESCO's "Transportation Expences"), total_demand_incl_losses, total_consumption

Up to 2025 the wind line is "Kartli Wind Power Plant", the one wind plant; from 2026 it is "Wind Power Plants", and a
"Solar power plants" line begins. In 2021 the line ESCO labels "Total Consumption" stands where later years have
"Supplied to the Consumers and Export", and equals supplied plus exports plus transit in every month; each such line is
placed by its arithmetic (supplied_and_export if it is supplied plus exports plus transit, total_consumption if it is
supplied plus the plants' losses plus the network losses), and a line that is neither stops the run.

Checks a month, within 0.01 million kWh: the kinds add to generation and the three hydro kinds to hydro; generation,
imports and transit to the total resource; the resource less the plants' losses to the delivery to the network;
distribution, direct customers and stopped plants to the supply to consumers; supply, exports and transit to
supplied_and_export; that plus the network losses to the total demand, which equals the delivery; and from 2022 the
supply, the plants' losses and the network losses to the total consumption. A month where one of these does not add
is ESCO's own figure: every figure is kept as published and the month and the check are named in the header. A cell
left blank in a month published has no row and is named too. Ten when written (session 2423):
- August to December 2025: the kinds are 0.3 to 1.3 million kWh under generation, a remainder with no line of its own
  (in 2026 ESCO adds a solar line of that size), and November 2025's total consumption is 0.085 over its parts;
- January 2023: distribution and direct customers are 320.82 million kWh under the supply to consumers;
- March 2023: the total demand is 318.05 million kWh over the delivery to the network;
- June 2021: inbound transit is blank, and the total resource is 35.468 million kWh over generation and imports.
More than twelve stops the run, as a sign the pages changed form. Each line's months add to its printed total within
0.15. A month with no figure (the current year's months not yet published) has no row. A
label not in the map, a value that is not a number or a failed check stops the run. Nothing is filled.

    python warehouse/connectors/esco_georgia.py [--offline] [--out-dir DIR]

Ceiling: one request a year's page (six), the current and the previous year's asked again, the others reused from
warehouse/raw/esco_georgia/; with --offline none.
esco.ge has no robots file (HTTP 404, session 2423). The balances for 2006 to 2020 are on pages of their own, not read
here (session 2423's ceiling). License: internal; session 2425's verdict, needs written permission: the site's footer reads "© 2016 ESCO ALL RIGHTS
RESERVED", and no page read states terms of reuse.
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

NAME = "esco_georgia_electricity_monthly"
CONNECTOR = "esco_georgia"
SOURCE = "esco_ge:actual_balance"
PAGE = "https://esco.ge/en/energy-balance/by-year-1"
YEARS = {2021: "elektroenergiis-balansi-2021", 2022: "elektroenergiis-balansi-2022", 2023: "balansi-2023",
         2024: "elektroenergiis-balansi-2024", 2025: "balance-2025", 2026: "balnsi-2026"}
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "Septem.", "October", "November", "December", "Total"]
SUPPLY = {"Generation": "generation", "Thermal plants": "generation_thermal", "Kartli Wind Power Plant": "generation_wind",
          "Wind Power Plants": "generation_wind", "Solar power plants": "generation_solar", "Hydro Plants": "generation_hydro",
          "Including the Regulatory": "generation_hydro_regulating", "Including the Seasonal": "generation_hydro_seasonal",
          "Including the Small power": "generation_hydro_small", "Import": "imports", "Transit": "transit_in",
          "Total Resource": "total_resource", "Plant Losses and Self-consumption": "plant_losses_self_consumption",
          "Delivery to the Network": "delivery_to_network"}
DEMAND = {"Supplied to the Consumers": "supplied_to_consumers", "Including the Distributiuon Comp.": "supplied_distribution",
          "Including the Direct Customers": "supplied_direct_customers",
          "Self-consumption of Stopped Plants": "self_consumption_stopped_plants", "Export": "exports", "Transit": "transit_out",
          "Supplied to the Consumers and Export": "supplied_and_export", "Transportation Expences": "network_losses",
          "Total Demand Including the Losses": "total_demand_incl_losses", "Total Consumption": None}
TOL = 0.01
MAX_GAPS = 12  # checks that fail or cells left blank in ESCO's own figures, named in the header; more stops the run


def cells(tr):
    return [html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", c))).strip() for c in re.findall(r"(?s)<t[hd][^>]*>(.*?)</t[hd]>", tr)]


def num(s, what):
    if not re.fullmatch(r"-?\d+(\.\d+)?", s):
        raise RuntimeError(f"{what}: not a number: {s!r}")
    return float(s)


def table(t, labels, year, side):
    """{variable: [12 values or None]} of one HTML table, each line's months checked against its printed total."""
    rows = [cells(tr) for tr in re.findall(r"(?s)<tr.*?</tr>", t)]
    if not rows or rows[0][1:] != MONTHS:
        raise RuntimeError(f"{year} {side}: the months are not ESCO's: {rows[0] if rows else None}")
    got, consumption = {}, None
    for r in rows[1:]:
        if len(r) != 14 or r[0] not in labels:
            raise RuntimeError(f"{year} {side}: a line not in the map: {r[:2]}")
        vals = [num(c, f"{year} {r[0]}") if c != "" else None for c in r[1:13]]
        total = num(r[13], f"{year} {r[0]} total")
        if abs(sum(v for v in vals if v is not None) - total) > 0.15:
            raise RuntimeError(f"{year} {side} {r[0]}: the months add to {sum(v for v in vals if v is not None):.3f}, the total is {total}")
        var = labels[r[0]]
        if var is None:
            consumption = vals
            continue
        if var in got:
            raise RuntimeError(f"{year} {side}: {var} twice")
        got[var] = vals
    return got, consumption


def parse_year(page, year):
    tabs = re.findall(r"(?s)<table.*?</table>", page)
    if len(tabs) < 2:
        raise RuntimeError(f"{year}: the page has no balance tables")
    s, _ = table(tabs[0], SUPPLY, year, "supply")
    d, cons = table(tabs[1], DEMAND, year, "demand")
    need_s = {"generation", "generation_thermal", "generation_wind", "generation_hydro", "generation_hydro_regulating",
              "generation_hydro_seasonal", "generation_hydro_small", "imports", "transit_in", "total_resource",
              "plant_losses_self_consumption", "delivery_to_network"}
    if not need_s <= set(s):
        raise RuntimeError(f"{year} supply: lines missing: {need_s - set(s)}")
    months = [m for m in range(12) if s["generation"][m] is not None]
    if months != list(range(len(months))) or not months:
        raise RuntimeError(f"{year}: the months published are not from January on: {months}")
    if cons is not None:  # placed once for the year by its arithmetic in the first month, then checked every month
        sup = lambda k, m: (d.get(k) or [0] * 12)[m] or 0.0  # noqa: E731
        sae0 = sup("supplied_to_consumers", 0) + sup("exports", 0) + sup("transit_out", 0)
        tc0 = sup("supplied_to_consumers", 0) + (s["plant_losses_self_consumption"][0] or 0.0) + sup("network_losses", 0)
        if "supplied_and_export" not in d and abs(cons[0] - sae0) <= TOL:
            d["supplied_and_export"] = cons
        elif abs(cons[0] - tc0) <= TOL:
            d["total_consumption"] = cons
        else:
            raise RuntimeError(f"{year}: \"Total Consumption\" ({cons[0]}) is neither supplied plus exports plus transit ({sae0:.3f}) nor supplied plus losses ({tc0:.3f})")
    out, gaps = {}, []
    for m in months:
        g = lambda k: (s.get(k) or [0] * 12)[m] or 0.0  # noqa: E731
        h = lambda k: (d.get(k) or [0] * 12)[m]  # noqa: E731
        checks = [
            (g("generation_thermal") + g("generation_wind") + g("generation_solar") + g("generation_hydro"), g("generation"), "the kinds and generation"),
            (g("generation_hydro_regulating") + g("generation_hydro_seasonal") + g("generation_hydro_small"), g("generation_hydro"), "the hydro kinds"),
            (g("generation") + g("imports") + g("transit_in"), g("total_resource"), "the total resource"),
            (g("total_resource") - g("plant_losses_self_consumption"), g("delivery_to_network"), "the delivery"),
            (h("supplied_distribution") + h("supplied_direct_customers") + h("self_consumption_stopped_plants"), h("supplied_to_consumers"), "the supply to consumers"),
            (h("total_demand_incl_losses"), g("delivery_to_network"), "the total demand and the delivery"),
        ]
        sae = h("supplied_to_consumers") + h("exports") + h("transit_out")
        checks += [(sae, h("supplied_and_export"), "supplied and export"),
                   (h("supplied_and_export") + h("network_losses"), h("total_demand_incl_losses"), "the total demand")]
        if "total_consumption" in d:
            checks.append((h("supplied_to_consumers") + g("plant_losses_self_consumption") + h("network_losses"), h("total_consumption"), "the total consumption"))
        for a, b, what in checks:
            if b is None:
                raise RuntimeError(f"{year}-{m + 1:02d}: {what}: a line has no figure")
            if abs(a - b) > TOL:
                gaps.append((year, m + 1, what, round(a, 3), b))  # ESCO's own figures that do not add; kept as published
        for var, vals in list(s.items()) + list(d.items()):
            if vals[m] is None:  # a blank cell in a month published: no row, named in the header, never filled
                gaps.append((year, m + 1, f"{var} is blank", None, None))
                continue
            out[(var, m + 1)] = vals[m]
    return out, gaps


def finish(rows, retrieved, vintage):
    t = pd.DataFrame([dict(entity="esco_ge:GE", variable=v, ts_utc=f"{y}-{m:02d}-01T00:00:00Z", value=round(x * 1000, 3), unit="MWh",
                           freq="P1M", geo="GE", market="", node="Georgia", source=SOURCE, source_url=url, retrieved_at=retrieved.get(y, ""),
                           vintage=vintage.get(y, "")) for (y, v, m), (x, url) in rows.items()], columns=COLS)
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("a key given twice")
    return t.sort_values(["variable", "ts_utc"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ESCO's actual electricity balance of Georgia a month, 2021 on")
    ap.add_argument("--offline", action="store_true", help="the saved pages only, no request")
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
        if not args.offline and (ip.paused("esco_ge") or ip.paused_host("esco.ge")):
            raise RuntimeError("ESCO is paused (warehouse/metadata/paused_sources.csv): not requested")
        rows, retrieved, vintage, gaps = {}, {}, {}, []
        this_year = dt.datetime.now(dt.timezone.utc).year
        for y, slug in sorted(YEARS.items()):
            url = f"{PAGE}/{slug}"
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline and y >= this_year - 1,
                                        headers=UA, timeout=120, pause=2)
            retrieved[y], vintage[y] = rec.get("retrieved_at") or "", ip.vintage_of(rec)
            got, g = parse_year(content.decode("utf-8", errors="replace"), y)
            gaps += g
            for (var, m), v in got.items():
                rows[(y, var, m)] = (v, url)
        if len(gaps) > MAX_GAPS:
            raise RuntimeError(f"{len(gaps)} months whose balance does not add up, more than {MAX_GAPS}: the pages may have changed form; first {gaps[:3]}")
        t = finish(rows, retrieved, vintage)
        header = [
            f"Energy Research Warehouse (ERW): Electricity Market Operator of Georgia (ESCO), actual electricity balance a month, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]} (session 2423)",
            "Shape: series (docs/datastandard.md v0). entity esco_ge:GE; unit MWh (ESCO's million kWh times 1,000); freq P1M; ts_utc the month's 1st; geo GE. variable: generation, generation_thermal, generation_wind, generation_solar (from 2026), generation_hydro and its regulating, seasonal and small plants, "
            "imports, transit_in, total_resource, plant_losses_self_consumption, delivery_to_network; supplied_to_consumers, supplied_distribution, supplied_direct_customers, self_consumption_stopped_plants, exports, transit_out, supplied_and_export, network_losses (ESCO's \"Transportation Expences\"), total_demand_incl_losses, total_consumption (from 2022).",
            f"{len(t)} rows. Each month's balance adds up within 0.01 million kWh (the kinds to generation, generation, imports and transit to the resource, the resource less the plants' losses to the delivery, the supply and exports plus the network losses to the total demand), except where named below, and each line's months to its printed total. "
            + "".join((f"ESCO's {y}-{m:02d} figures do not add in one place ({what}: {a:,.3f} against the printed {b:,.3f} million kWh); every figure is kept as published. " if a is not None
                       else f"ESCO's {y}-{m:02d} {what}: no row. ") for y, m, what, a, b in gaps)
            + "Up to 2025 the wind line is the Kartli Wind Power Plant alone. ESCO's 2021 \"Total Consumption\" line is supplied plus exports plus transit and is written as supplied_and_export. Months not yet published have no row. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/esco_georgia.py; each year's page retrieved as its source_url's rows say",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Electricity Market Operator (ESCO), Energy Balance, Actual Balance, the years {min(YEARS)} to {max(YEARS)}, {PAGE}",
            f"  access: {PAGE}/<year's page> (one a year)",
            "License: internal. ESCO's site reads \"© 2016 ESCO ALL RIGHTS RESERVED\" and states no terms of reuse; session 2425's verdict: needs written permission. Cite: Electricity Market Operator (ESCO), Georgia, Actual Balance.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Electricity Market Operator of Georgia (ESCO)",
                                    report="Energy Balance, Actual Balance, a page a year (supply and consumption a month)",
                                    report_url=PAGE, document_list=PAGE, license="internal", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]}")
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
