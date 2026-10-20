#!/usr/bin/env python3
"""JEDI's jobs, earnings and output per MW, by technology, state and phase (session 345): the table nlr_jedi_multipliers.

Energy Research Warehouse (ERW). NLR's Jobs and Economic Development Impact (JEDI) models, one Excel workbook per
technology, estimate what building and running a power plant does for a state's economy: jobs, earnings and output,
each split into onsite, supply chain and induced effects. The economic impact tool (/impact, tool 17) reads this table.

The chain prompt names the table jedi_multipliers; a series table's name has three parts (docs/datastandard.md), so it
is nlr_jedi_multipliers (source nlr, the JEDI models, their multipliers), as battery_sourced_ranges was named in
session 306.

    python warehouse/connectors/jedi_multipliers.py --pull   # ask NLR for the four workbooks (four requests)
    .venv-jedi\\Scripts\\python.exe -I warehouse/connectors/jedi_recalc.py   # JEDI's formulas for every location
    python warehouse/connectors/jedi_multipliers.py          # the table, from the workbooks and that step's files

How a figure is made. Each workbook is saved with one project in one state (wind: 300 MW in Connecticut) and holds
that project's results only; the multipliers of every state sit in its hidden sheet Multipliers, per million dollars
of spending. jedi_recalc.py evaluates the workbook's own formulas with Project Location set to each location of the
model's own list and nothing else changed, after checking that the saved project, computed from the workbook's
constants, gives every saved figure. This script divides each summary line by the project's MW: a value is per MW of
JEDI's default project, at JEDI's default costs and local shares, in the model's dollar year. Nothing is filled:
a location where JEDI's own answer is an Excel error (the gas model's #DIV/0! for DC and Hawaii) has no row, and
battery storage, for which NLR publishes no JEDI model, has none.

The one setting changed besides the location: the PV model's System Application is set to its own "Utility" option
(the prompt asks for utility-scale PV; the workbook is saved with a residential project). JEDI then takes its own
utility defaults for system size and cost.

Terms (read 20 October 2026, runs/s345/pages/): NLR's data terms (https://www.nlr.gov/disclaimer, the same page as
license read 65, the same SHA-256): use and copy without fee, the notice kept, DOE/NLR/ALLIANCE credited, as is. The
workbooks hold no user agreement tab of their own; the gas and geothermal FAQ sheets mention one accepted at download,
and the download pages ask for no registration today. License: public, with that credit.

Shape: series. entity nlr_jedi:<technology>:<state, or us>:<phase>:<effect>; variable jobs, earnings or output;
ts_utc 1 January of the model's dollar year, freq P1Y; geo US-<state> or US.
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "nlr_jedi_multipliers"
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
RAW = os.path.join(ROOT, "warehouse", "raw", "nlr_jedi")
RECALC = os.path.join(RAW, "recalc")
SOURCE = "nlr:jedi"
PUBLISHER = "National Laboratory of the Rockies (NLR, formerly NREL)"
PAGE = "https://www.nlr.gov/analysis/jedi/models"
TERMS = "https://www.nlr.gov/disclaimer"
NOTICE = ("NLR's data terms (https://www.nlr.gov/disclaimer): the user is granted the right, without any fee or cost, to use "
          "or copy the Data, provided that this entire notice appears in all copies of the Data; credit DOE/NLR/ALLIANCE; "
          "the Data are provided as is")
# technology -> the workbook, where NLR lists it, its model name, the cells of its version and multiplier year, and the
# summary's units (the recalculation's own MODELS holds the cells of each line)
MODELS = {
    "land_based_wind": dict(
        file="01d-jedi-land-based-wind-model-rel-w6-28-19.xlsm", page="https://www.nlr.gov/analysis/jedi/wind",
        url="https://www.nlr.gov/docs/libraries/analysis/01d-jedi-land-based-wind-model-rel-w6-28-19.xlsm?sfvrsn=e1d95728_2",
        model="JEDI Land-based Wind Model", version=("About JEDI", "B9"), unit_note="millions of dollars"),
    "utility_pv": dict(
        file="jedi-pv-model.xlsm", page="https://www.nlr.gov/analysis/jedi/pv",
        url="https://www.nlr.gov/docs/libraries/analysis/jedi-pv-model.xlsm?sfvrsn=837efebd_2",
        model="JEDI Photovoltaics Model", version=("About JEDI", "A6"), unit_note="thousands of dollars"),
    "natural_gas": dict(
        file="01d-jedi-ngas-model_rel-ng4-17-17.xlsm", page="https://www.nlr.gov/analysis/jedi/natural-gas",
        url="https://www.nlr.gov/docs/libraries/analysis/01d-jedi-ngas-model_rel-ng4-17-17.xlsm?sfvrsn=d9ff898_2",
        model="JEDI Natural Gas Model", version=("About JEDI", "B9"), unit_note="millions of dollars"),
    "geothermal": dict(
        file="01d-jedi-geothermal-model-rel-gt12-23-16.xlsm", page="https://www.nlr.gov/analysis/jedi/geothermal",
        url="https://www.nlr.gov/docs/libraries/analysis/01d-jedi-geothermal-model-rel-gt12-23-16.xlsm",
        model="JEDI Geothermal Model", version=("About", "A6"), unit_note="millions of dollars"),
}
NOT_HELD = {"battery_storage": "NLR publishes no JEDI model for battery storage: the thirteen models listed on "
                               "https://www.nlr.gov/analysis/jedi/models (read 20 October 2026) have none, so no row is written"}
UNITS = {("construction", "jobs"): "FTE-year/MW", ("operations", "jobs"): "FTE/MW",
         ("construction", "earnings"): "USD/MW", ("operations", "earnings"): "USD/MW-year",
         ("construction", "output"): "USD/MW", ("operations", "output"): "USD/MW-year"}
STATES = {
    "ALABAMA": "AL", "ALASKA": "AK", "ARIZONA": "AZ", "ARKANSAS": "AR", "CALIFORNIA": "CA", "COLORADO": "CO",
    "CONNECTICUT": "CT", "DELAWARE": "DE", "DISTRICT OF COLUMBIA": "DC", "FLORIDA": "FL", "GEORGIA": "GA", "HAWAII": "HI",
    "IDAHO": "ID", "ILLINOIS": "IL", "INDIANA": "IN", "IOWA": "IA", "KANSAS": "KS", "KENTUCKY": "KY", "LOUISIANA": "LA",
    "MAINE": "ME", "MARYLAND": "MD", "MASSACHUSETTS": "MA", "MICHIGAN": "MI", "MINNESOTA": "MN", "MISSISSIPPI": "MS",
    "MISSOURI": "MO", "MONTANA": "MT", "NEBRASKA": "NE", "NEVADA": "NV", "NEW HAMPSHIRE": "NH", "NEW JERSEY": "NJ",
    "NEW MEXICO": "NM", "NEW YORK": "NY", "NORTH CAROLINA": "NC", "NORTH DAKOTA": "ND", "OHIO": "OH", "OKLAHOMA": "OK",
    "OREGON": "OR", "PENNSYLVANIA": "PA", "RHODE ISLAND": "RI", "SOUTH CAROLINA": "SC", "SOUTH DAKOTA": "SD",
    "TENNESSEE": "TN", "TEXAS": "TX", "UTAH": "UT", "VERMONT": "VT", "VIRGINIA": "VA", "WASHINGTON": "WA",
    "WEST VIRGINIA": "WV", "WISCONSIN": "WI", "WYOMING": "WY", "UNITED STATES": "",
}
# a location as a model's own list spells it, where the spelling is not the state's name (x_location keeps JEDI's word)
ALIASES = {"NORTH DAKOTO": "ND", "SOUTH DAKOTO": "SD"}  # the gas model's list
X_COLS = ["x_technology", "x_state", "x_location", "x_phase", "x_effect", "x_model", "x_version", "x_file", "x_sheet",
          "x_cells", "x_project_mw", "x_mw_basis", "x_dollar_year", "x_multiplier_data", "x_local_share",
          "x_local_share_cells", "x_settings", "x_method"]


def recalc_spec():
    """The recalculation step's MODELS (its cells of each line), read from its file without importing pycel."""
    import ast
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "jedi_recalc.py"), encoding="utf-8").read()
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "MODELS":
            # the assignment alone, with nothing but dict() in reach: no import of pycel, no other code of the step
            return eval(compile(ast.Expression(node.value), "jedi_recalc.py", "eval"), {"__builtins__": {}, "dict": dict})
    raise RuntimeError("jedi_recalc.py holds no MODELS")


def pull(log):
    """Four requests, one a workbook, kept as they came. NLR's robots file allows every path (read 20 October 2026)."""
    import requests
    os.makedirs(RAW, exist_ok=True)
    for tech, m in MODELS.items():
        r = requests.get(m["url"], headers={"User-Agent": "ERW research (Energy Research Warehouse)"}, timeout=300)
        r.raise_for_status()
        with open(os.path.join(RAW, m["file"]), "wb") as f:
            f.write(r.content)
        log(f"pulled {m['url']}: {len(r.content):,} bytes")


def facts(path, m):
    """The release number and the multipliers' data year, as the workbook states them."""
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheet, cell = m["version"]
    version = str(wb[sheet][cell].value or "").replace("Release Number:", "").strip()
    mult = wb["Multipliers"]
    year = mult["D2"].value
    note = ""
    for row in mult.iter_rows(min_row=200, max_row=mult.max_row, max_col=3, values_only=True):
        t = row[2]
        if isinstance(t, str) and "IMPLAN" in t and "state data" in t:
            note = " ".join(t.replace("®", "").replace("�", "").split())
            break
    if not version:
        raise RuntimeError(f"{m['file']}: no release number at {sheet}!{cell}")
    return version, f"Multipliers!D2 (Year of Data) {year}" + (f"; the sheet's note: {note}" if note else "")


def rows_for(tech, m, spec, rec, version, mult, sha, kept, log):
    out = []
    summary = spec["summary"]
    for loc, r in rec["results"].items():
        state = STATES.get(loc.strip().upper(), ALIASES.get(loc.strip().upper()))
        if state is None:
            raise RuntimeError(f"{tech}: JEDI's location {loc!r} is not a state this script knows")
        mw = r[spec["mw"]] * spec["mw_scale"]
        if not mw or mw <= 0:
            raise RuntimeError(f"{tech} at {loc!r}: the project's MW ({spec['mw']}) is {r[spec['mw']]!r}")
        dollar_year = int(r[spec["dollar_year"]])
        shares = {}
        for phase, (num, den) in spec["local"].items():
            shares[phase] = (r[num] / r[den] if r[den] else None, f"{num} / {den}")
        saved = loc == rec["saved_location"]
        method = ("the workbook's saved project, computed from its constants (every saved figure reproduced)" if saved
                  and not rec["settings"] else
                  "JEDI's formulas computed from the workbook's constants with Project Location set to this location"
                  + (f" and {', '.join(f'{k} = {v}' for k, v in rec['settings'].items())}" if rec["settings"] else "")
                  + "; nothing else changed (warehouse/connectors/jedi_recalc.py)")
        for phase, effect, row, _ in spec["rows"]:
            for measure, col in (("jobs", "B"), ("earnings", "C"), ("output", "D")):
                ref = f"{summary}!{col}{row}"
                v = r[ref]
                if not isinstance(v, (int, float)):
                    raise RuntimeError(f"{tech} at {loc!r}: {ref} is {v!r}")
                value = v / mw * (1 if measure == "jobs" else spec["scale"])
                share, share_cells = shares[phase]
                out.append(dict(
                    entity=f"nlr_jedi:{tech}:{(state or 'us').lower()}:{phase}:{effect}", variable=measure,
                    ts_utc=f"{dollar_year}-01-01T00:00:00Z", value=round(value, 6), unit=UNITS[(phase, measure)],
                    freq="P1Y", geo=f"US-{state}" if state else "US", market="", node="", source=SOURCE,
                    source_url=m["url"], retrieved_at=kept, vintage="",
                    x_technology=tech, x_state=state, x_location=loc.strip(), x_phase=phase, x_effect=effect,
                    x_model=m["model"], x_version=version, x_file=m["file"], x_sheet=summary,
                    x_cells=f"{ref} / {spec['mw']}" + (f" x {spec['mw_scale']:g}" if spec["mw_scale"] != 1 else ""),
                    x_project_mw=round(mw, 6), x_mw_basis=spec["mw_basis"], x_dollar_year=str(dollar_year),
                    x_multiplier_data=mult, x_local_share="" if share is None else round(share, 6),
                    x_local_share_cells=share_cells, x_settings="; ".join(f"{k} = {v}" for k, v in rec["settings"].items()),
                    x_method=method))
        # the project's MW and each phase's local share, as rows of their own: the site reads only entity, variable, ts_utc
        # and value from the live set (its series table has no room for x_ columns), and the page shows both
        common = dict(ts_utc=f"{dollar_year}-01-01T00:00:00Z", freq="P1Y", geo=f"US-{state}" if state else "US", market="",
                      node="", source=SOURCE, source_url=m["url"], retrieved_at=kept, vintage="", x_technology=tech, x_state=state,
                      x_location=loc.strip(), x_model=m["model"], x_version=version, x_file=m["file"], x_sheet=summary,
                      x_project_mw=round(mw, 6), x_mw_basis=spec["mw_basis"], x_dollar_year=str(dollar_year),
                      x_multiplier_data=mult, x_settings="; ".join(f"{k} = {v}" for k, v in rec["settings"].items()), x_method=method)
        out.append(dict(common, entity=f"nlr_jedi:{tech}:{(state or 'us').lower()}:all:project", variable="project_mw",
                        value=round(mw, 6), unit="MW", x_phase="all", x_effect="project",
                        x_cells=spec["mw"] + (f" x {spec['mw_scale']:g}" if spec["mw_scale"] != 1 else ""),
                        x_local_share="", x_local_share_cells=""))
        for phase, (share, share_cells) in shares.items():
            if share is None:
                continue
            out.append(dict(common, entity=f"nlr_jedi:{tech}:{(state or 'us').lower()}:{phase}:spending", variable="local_share",
                            value=round(share, 6), unit="ratio", x_phase=phase, x_effect="spending", x_cells=share_cells,
                            x_local_share=round(share, 6), x_local_share_cells=share_cells))
    log(f"{tech}: {len(out)} rows from {len(rec['results'])} locations"
        + (f"; JEDI gives an Excel error at {sorted(rec.get('errors', {}))}, no row" if rec.get("errors") else ""))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="JEDI's jobs, earnings and output per MW (session 345)")
    ap.add_argument("--pull", action="store_true", help="ask NLR for the four workbooks first (four requests)")
    a = ap.parse_args(argv)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    results = []
    try:
        if ip.paused_host("www.nlr.gov"):
            raise RuntimeError("www.nlr.gov is paused (warehouse/metadata/paused_sources.csv)")
        if a.pull:
            pull(log)
        spec_all = recalc_spec()
        recs, kept_files, errors_all = [], [], {}
        for tech, m in MODELS.items():
            path = os.path.join(RAW, m["file"])
            rp = os.path.join(RECALC, f"{tech}.json")
            if not os.path.exists(path):
                raise RuntimeError(f"warehouse/raw/nlr_jedi/{m['file']} is not on this machine; run with --pull")
            if not os.path.exists(rp):
                raise RuntimeError(f"warehouse/raw/nlr_jedi/recalc/{tech}.json is absent; run jedi_recalc.py first")
            sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
            rec = json.load(open(rp, encoding="utf-8"))
            if rec["sha256"] != sha:
                raise RuntimeError(f"{tech}: the recalculation was made from another copy of {m['file']}; run jedi_recalc.py again")
            kept = dt.datetime.fromtimestamp(os.path.getmtime(path), dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            version, mult = facts(path, m)
            recs += rows_for(tech, m, spec_all[tech], rec, version, mult, sha, kept, log)
            kept_files.append(f"{m['file']} (release {version}, SHA-256 {sha[:16]}, kept {kept}; recalculated "
                              f"{rec['evaluated_at']}, {rec['reproduced_cells']} saved figures reproduced)")
            errors_all.update({f"{tech}:{k.strip()}": "Excel error" for k in rec.get("errors", {})})
        df = pd.DataFrame(recs)
        if df.duplicated(ip.SERIES_KEY).any():
            raise RuntimeError("an (entity, variable, ts_utc) is given twice")
        cols = ip.SERIES_COLS + X_COLS
        header = [
            "Energy Research Warehouse (ERW): JEDI's jobs, earnings and output per MW, by technology, state, phase and effect (session 345)",
            "Shape: series (docs/datastandard.md v0). entity nlr_jedi:<technology>:<state or us>:<phase>:<effect>; variable jobs, earnings or output; "
            "ts_utc 1 January of the model's dollar year. Construction jobs are job-years (1 FTE = 2,080 hours) over the build per MW; "
            "operations figures are each year's. Per MW of JEDI's default project (x_project_mw), at JEDI's default costs and local shares. "
            "Two more rows a location: <...>:all:project, variable project_mw (the default project's MW), and <...>:<phase>:spending, "
            "variable local_share (JEDI's local spending over the phase's cost).",
            f"Source: {SOURCE} {PUBLISHER}, Jobs and Economic Development Impact (JEDI) models, {PAGE}",
            "Kept: " + "; ".join(kept_files),
            "Method: each workbook's own formulas, evaluated for each location of its own list (warehouse/connectors/jedi_recalc.py, pycel), "
            "after the saved project computed from its constants gave every saved figure; the PV model's System Application set to its own Utility option",
            "Not written: " + "; ".join(f"{k}: {v}" for k, v in NOT_HELD.items())
            + ("; JEDI's own answer an Excel error, so no row: " + ", ".join(sorted(errors_all)) if errors_all else ""),
            "License: public. " + NOTICE + " (read 2026-10-20, the same page and SHA-256 as license read 65)",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/jedi_multipliers.py",
            f"Run log: warehouse/output/logs/{NAME}_{run_id}.log",
        ]
        ip.write_snapshot(df[cols], NAME, header, log, cols)
        ip.update_sources([dict(source=SOURCE, publisher=PUBLISHER,
                                report="Jobs and Economic Development Impact (JEDI) models: land-based wind W9.14.18, "
                                       "photovoltaics PV05.20.21, natural gas NG4.17.17, geothermal GT12.23.16",
                                report_url=PAGE, document_list=PAGE, license="public", tables=[NAME])])
        log(f"wrote {len(df)} rows")
        print(f"{NAME}: {len(df)} rows, {df['x_technology'].nunique()} technologies, {df['x_location'].nunique()} locations")
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(df)} rows"))
    except Exception as exc:
        log(f"FAILED, no output file written: {type(exc).__name__}: {exc}")
        print(f"{NAME} FAILED, no output file written: {type(exc).__name__}: {exc}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=str(exc)[:300]))
    ip.write_status(NAME, run_id, results)
    log.close()
    return 1 if any(r["status"] == "failed" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
