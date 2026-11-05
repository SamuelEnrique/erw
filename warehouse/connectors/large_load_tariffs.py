#!/usr/bin/env python3
"""Large loads' filed tariffs: the registry of what a 100 MW to 1 GW load pays to connect and take delivery (session
2871, chain 147).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/utility_large_load_tariffs.csv, the name
the All grids tab's builder already reads (warehouse/derived/siting_page.py, tariffs_file, session 730), from the
registry files sessions fill by reading each utility's filed tariff:

    warehouse/sources/large_load_tariffs/<utility>_<schedule>.yaml    one file a schedule (README.md there: the form)

No request is made here: a session reads the filed tariff (the commission's docket or the utility's filed tariff book,
robots and terms first), writes each figure into the schedule's file with the page it is printed on and the words it is
printed in, and this connector turns the files into rows. A figure is kept as the schedule prints it (x_printed); its
value is that figure in the table's unit, converted only between units (cents to dollars, kWh to MWh, kW to MW), never
derived, summed or estimated. A figure the schedule does not print has no row.

    entity      filed:<EIA utility id>:<schedule slug>; node the schedule's name; geo US-<state>
    ts_utc      the schedule's effective date, 00:00:00Z; freq blank (a tariff in force from that day)
    variable    min_demand_mw (MW), the smallest load the schedule takes
                demand_charge (USD/kW-month), a schedule's one delivery demand charge where it prints one; where it
                  prints parts: demand_charge_transmission, demand_charge_distribution, demand_charge_generation
                energy_charge (USD/MWh), where the schedule prints one energy charge for delivery or bundled service
                fixed_charge (USD, a month), the customer or facilities charge
                min_contract_years (year), the shortest contract term the schedule takes
                min_bill_pct (pct), a minimum bill or take-or-pay share of contract demand, where printed as a share
                collateral_months (month), collateral stated as months of bills
                exit_fee_months (month), an exit fee stated as months of minimum bills
    source_url  the filed document's address; x_page the page of that document the figure is on
    x_*         x_eia_id, x_utility, x_sector, x_state, x_grid, x_schedule, x_tariff_sheet, x_voltage, x_commission,
                x_docket, x_document, x_page, x_printed, and the schedule's terms in its own words: x_min_bill,
                x_collateral, x_exit_fee, x_ramp, x_term

The validator refuses a row of this table without source_url or x_page (erw_validate.py, session 2871): every figure
carries its filing. License: public, row by row: each row cites a commission's filing, a public regulatory record. A
utility site whose terms bar the reader is not read; the commission's docket copy is. The OpenEI connector
(openei_large_load_tariffs.py, session 670, never run: no key) writes the same table under entities openei_urdb:*; the
two merge by (entity, variable, ts_utc) and never overwrite each other's rows.

    python warehouse/connectors/large_load_tariffs.py              # the table (data lock)
    python warehouse/connectors/large_load_tariffs.py --check      # read and check the registry, write nothing
    python warehouse/connectors/large_load_tariffs.py --out-dir D  # a trial: the table under D (no data lock)

Method: docs/methods/large_load_tariffs.md.
"""

import argparse
import datetime as dt
import glob
import os
import re
import sys
import traceback

import pandas as pd
import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
REGISTRY = os.path.join(ROOT, "warehouse", "sources", "large_load_tariffs")
NAME = "utility_large_load_tariffs"
SOURCE = "filed:large_load_tariffs"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/large_load_tariffs.md"
UNITS = {"min_demand_mw": "MW", "demand_charge": "USD/kW-month", "demand_charge_transmission": "USD/kW-month",
         "demand_charge_distribution": "USD/kW-month", "demand_charge_generation": "USD/kW-month", "energy_charge": "USD/MWh",
         "fixed_charge": "USD", "min_contract_years": "year", "min_bill_pct": "pct", "collateral_months": "month",
         "exit_fee_months": "month"}
FIELDS = ("utility", "eia_id", "state", "grid", "sector", "schedule", "tariff_sheet", "effective", "commission", "document",
          "document_url", "retrieved_at", "license", "figures")
TERMS = ("min_bill", "collateral", "exit_fee", "ramp", "term")
X_COLS = ["x_eia_id", "x_utility", "x_sector", "x_state", "x_grid", "x_schedule", "x_tariff_sheet", "x_voltage", "x_commission",
          "x_docket", "x_document", "x_page", "x_printed"] + [f"x_{t}" for t in TERMS]
COLS = ip.SERIES_COLS + X_COLS
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def slug(text):
    return re.sub(r"[^a-z0-9]+", "_", str(text).lower()).strip("_")[:60]


def words(v):
    """A term as the schedule prints it: {text, page} or a string; '' when absent."""
    if v is None:
        return ""
    if isinstance(v, dict):
        t, p = str(v.get("text") or "").strip(), v.get("page")
        return f"{t} (p. {p})" if t and p not in (None, "") else t
    return " ".join(str(v).split())


def check(reg, path):
    """The problems of one schedule's file, as sentences; [] when it can be written."""
    bad = [f"no {k}" for k in FIELDS if reg.get(k) in (None, "", [])]
    if not DATE_RE.match(str(reg.get("effective") or "")):
        bad.append(f"effective {reg.get('effective')!r} is not YYYY-MM-DD")
    if not TS_RE.match(str(reg.get("retrieved_at") or "")):
        bad.append(f"retrieved_at {reg.get('retrieved_at')!r} is not YYYY-MM-DDTHH:MM:SSZ")
    if not re.match(r"^[A-Z]{2}$", str(reg.get("state") or "")):
        bad.append(f"state {reg.get('state')!r} is not a two-letter code")
    if not str(reg.get("document_url") or "").startswith(("http://", "https://")):
        bad.append("document_url is not an address")
    if str(reg.get("license") or "") != "public":
        bad.append(f"license {reg.get('license')!r}: only a public filing is written here")
    seen = set()
    for i, f in enumerate(reg.get("figures") or []):
        v = f.get("variable")
        if v not in UNITS:
            bad.append(f"figure {i}: variable {v!r} is not one of {sorted(UNITS)}")
        if v in seen:
            bad.append(f"figure {i}: {v} twice")
        seen.add(v)
        if not isinstance(f.get("value"), (int, float)) or isinstance(f.get("value"), bool):
            bad.append(f"figure {i} ({v}): value {f.get('value')!r} is not a number")
        if f.get("page") in (None, ""):
            bad.append(f"figure {i} ({v}): no page")
        if not str(f.get("printed") or "").strip():
            bad.append(f"figure {i} ({v}): no printed words")
    if "demand_charge" in seen and seen & {"demand_charge_transmission", "demand_charge_distribution", "demand_charge_generation"}:
        bad.append("demand_charge beside its parts: a schedule prints one or the parts")
    return [f"{os.path.basename(path)}: {b}" for b in bad]


def read_registry(folder=REGISTRY):
    """(the schedules' files as dicts with their paths, the problems)."""
    regs, problems = [], []
    for p in sorted(glob.glob(os.path.join(folder, "*.yaml"))):
        with open(p, encoding="utf-8") as fh:
            reg = yaml.safe_load(fh) or {}
        # YAML reads an unquoted date or time as one: written back as the registry's text
        for k in ("effective", "retrieved_at"):
            v = reg.get(k)
            if isinstance(v, dt.datetime):
                reg[k] = v.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if v.tzinfo else v.strftime("%Y-%m-%dT%H:%M:%SZ")
            elif isinstance(v, dt.date):
                reg[k] = v.isoformat()
        problems += check(reg, p)
        regs.append((p, reg))
    return regs, problems


def rows(regs):
    """The table's rows from the schedules' files."""
    out = []
    for p, reg in regs:
        eia = str(reg["eia_id"]).strip()
        ent = f"filed:{eia}:{slug(reg['schedule'])}"
        common = {"ts_utc": f"{reg['effective']}T00:00:00Z", "freq": "", "geo": f"US-{reg['state']}", "market": "", "node": str(reg["schedule"]),
                  "source": SOURCE, "source_url": str(reg["document_url"]), "retrieved_at": str(reg["retrieved_at"]), "vintage": "",
                  "x_eia_id": eia, "x_utility": str(reg["utility"]), "x_sector": str(reg["sector"]), "x_state": str(reg["state"]),
                  "x_grid": str(reg["grid"]), "x_schedule": str(reg["schedule"]), "x_tariff_sheet": str(reg["tariff_sheet"]),
                  "x_voltage": words(reg.get("voltage")), "x_commission": str(reg["commission"]), "x_docket": str(reg.get("docket") or ""),
                  "x_document": str(reg["document"])}
        terms = reg.get("terms") or {}
        common.update({f"x_{t}": words(terms.get(t)) for t in TERMS})
        for f in reg["figures"]:
            v = f["variable"]
            out.append({"entity": ent, "variable": v, "value": float(f["value"]), "unit": UNITS[v], "x_page": str(f["page"]),
                        "x_printed": " ".join(str(f["printed"]).split()), **common})
    d = pd.DataFrame(out, columns=COLS).fillna("")
    return d.sort_values(["x_grid", "x_utility", "entity", "variable"]).reset_index(drop=True)


def header(d, run_id):
    utilities = d.drop_duplicates("x_eia_id")[["x_utility", "x_grid"]].itertuples(index=False) if len(d) else []
    return [
        "Energy Research Warehouse (ERW): large loads' filed tariffs, one row a figure a schedule prints (session 2871, chain 147)",
        "Shape: series (docs/datastandard.md v0). entity filed:<EIA utility id>:<schedule>; ts_utc the schedule's effective date at 00:00:00Z; "
        "variables " + ", ".join(f"{k} ({u})" for k, u in UNITS.items()) + ". value is the printed figure (x_printed) in the unit, "
        "converted only between units; nothing is derived. source_url is the filed document, x_page its page.",
        f"Utilities: {len(d['x_eia_id'].unique()) if len(d) else 0}; schedules: {d['entity'].nunique() if len(d) else 0}: "
        + "; ".join(f"{u} ({g})" for u, g in utilities),
        "Source: the registry warehouse/sources/large_load_tariffs/ (one file a schedule, each figure with its page and words), "
        "filled by reading each commission's filed copy. No request is made by this connector.",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/large_load_tariffs.py; each row's retrieved_at is when its filing was read",
        f"Method: {METHOD_URL}",
        "License: public, row by row: each row cites a commission's filing (a filed tariff is a public regulatory record).",
    ]


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: large loads' filed tariffs from the registry (session 2871)")
    ap.add_argument("--check", action="store_true", help="read and check the registry; write nothing")
    ap.add_argument("--out-dir", help="a trial: write under this directory (no data lock)")
    ap.add_argument("--registry", default=REGISTRY, help="the registry folder (a test's)")
    a = ap.parse_args(argv)
    regs, problems = read_registry(a.registry)
    for p in problems:
        print(f"REFUSED: {p}")
    if problems:
        print(f"{NAME} FAILED: {len(problems)} problems in the registry; nothing written")
        return 1
    d = rows(regs)
    print(f"{NAME}: {len(regs)} schedules, {len(d)} rows, {d['x_eia_id'].nunique() if len(d) else 0} utilities")
    if a.check:
        return 0
    if d.empty:
        print(f"{NAME} SKIPPED: the registry holds no schedule; nothing written")
        return int(os.environ.get("ERW_SKIP_EXIT", "75"))
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    try:
        ip.write_csv(d, NAME, header(d, run_id), log, cols=COLS)
        if not a.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="the state commissions (filed tariffs), read into the ERW's registry",
                                    report="Large loads' filed tariffs (warehouse/sources/large_load_tariffs)", report_url=METHOD_URL,
                                    document_list="", license="public", tables=[NAME])])
    except Exception as exc:
        print(f"{NAME} FAILED: {type(exc).__name__}: {exc}")
        log(traceback.format_exc())
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
