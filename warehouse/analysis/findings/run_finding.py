#!/usr/bin/env python3
"""Run one Automated Analysis finding and write its card (session 170).

Energy Research Warehouse (ERW).

    python warehouse/analysis/findings/run_finding.py --list
    python warehouse/analysis/findings/run_finding.py batteries_lunch --param hub=HB_NORTH
    python warehouse/analysis/findings/run_finding.py gas_sets_price --in-dir C:/Users/lossa/Documents/erw/warehouse/output --out-dir runs/x
    python warehouse/analysis/findings/run_finding.py --tables            # the tables every finding reads, one pattern (roundup.yml)

Writes, into --out-dir (default site/data/findings for the card and site/public/findings for the downloads):
    <id>.json       the card: title, subtitle, chart, callouts, why, footnote, numbers (every number on the card, keyed),
                    the effect table for an econometric finding, the downloads' names and the CSV's hash
    <csv name>      the data as CSV (study_year_topic_word.csv)
    <id>.py         the Python that computed it (this folder's module, as run)
    <id>.do         the Stata do-file to the owner's rules
A finding with non-default inputs is written as <id>__<k-v>__<k-v>.json, so the default card stands. A table that is
not on this machine is a NoData exit (3), named; nothing is filled in. Exit 0 written, 1 failed, 2 bad input.
"""

import argparse
import importlib
import json
import os
import re
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import findings_common as common  # noqa: E402

FINDINGS = ["batteries_lunch", "gas_sets_price", "queue_divorce", "peak_hour_moved", "who_rescues_whom", "negative_prices_west", "batteries_curtailment"]  # session 174: four more
FINDINGS += ["batteries_lunch_grids", "peak_hour_grids", "batteries_curtailment_hourly"]  # session 182: every grid with public prices; CAISO by the hour
CARD_DIR = os.path.join(ROOT, "site", "data", "findings")
DOWNLOAD_DIR = os.path.join(ROOT, "site", "public", "findings")


def load(name):
    if name not in FINDINGS:
        raise ValueError(f"no finding named {name!r}; the findings are {', '.join(FINDINGS)}")
    return importlib.import_module(name)


def load_all():
    return [load(n) for n in FINDINGS]


def catalogue():
    """What /analysis shows a person to pick from: each finding, its kind, its inputs with choices and words."""
    out = []
    for m in load_all():
        out.append({"id": m.NAME, "title": m.TITLE, "kind": m.KIND, "tables": m.TABLES,
                    "inputs": {k: {"label": v["label"], "default": v["default"], "choices": v["choices"], "words": v.get("words", {})}
                               for k, v in m.INPUTS.items()}})
    return out


def card_id(name, params, mod):
    """The card's file id: the finding's name, then each non-default input as __k-v."""
    parts = [name]
    for k, spec in mod.INPUTS.items():
        v = params.get(k, spec["default"])
        if str(v) != str(spec["default"]):
            parts.append(f"{k}-{re.sub(r'[^A-Za-z0-9.]+', '_', str(v))}")
    return "__".join(parts)


def coerce(mod, params):
    out = {}
    for k, spec in mod.INPUTS.items():
        v = params.get(k, spec["default"])
        kind = type(spec["default"])
        try:
            v = kind(v) if kind is not bool else v
        except (TypeError, ValueError):
            raise ValueError(f"input {k}={v!r} is not a {kind.__name__}")
        if spec["choices"] and v not in spec["choices"]:
            raise ValueError(f"input {k}={v!r} is not one of {spec['choices']}")
        out[k] = v
    return out


def run(name, params, in_dir=None, card_dir=None, download_dir=None, log=print):
    mod = load(name)
    params = coerce(mod, params or {})
    cid = card_id(name, params, mod)
    log(f"finding {name} {params} -> {cid}")
    rows, meta = mod.compute(params, in_dir)
    card = mod.card(rows, params, meta)
    card["card_id"] = cid
    card["meta"] = meta
    card_dir = card_dir or CARD_DIR
    download_dir = download_dir or DOWNLOAD_DIR
    os.makedirs(download_dir, exist_ok=True)
    csv_name = mod.CSV_NAME if cid == name else f"{mod.CSV_NAME[:-4]}__{cid[len(name) + 2:]}.csv"
    path = common.write_card(card, rows, mod.SOURCE_PATH, mod.stata(params), download_dir, cid, csv_name)
    os.makedirs(card_dir, exist_ok=True)
    final = os.path.join(card_dir, cid + ".json")
    if os.path.abspath(final) != os.path.abspath(path):
        os.replace(path, final)
    log(f"  wrote {final}; downloads {csv_name}, {cid}.py, {cid}.do in {download_dir}")
    return final, card


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW Automated Analysis: run one finding (session 170)")
    ap.add_argument("name", nargs="?")
    ap.add_argument("--param", action="append", default=[], help="k=v, one per input")
    ap.add_argument("--in-dir", help="the warehouse's output directory (default ERW_DATA_DIR or warehouse/output)")
    ap.add_argument("--out-dir", help="write the card and the downloads here (default site/data/findings and site/public/findings)")
    ap.add_argument("--list", action="store_true", help="print the catalogue as JSON")
    ap.add_argument("--tables", action="store_true", help="print one regex of every table the findings read")
    a = ap.parse_args(argv)
    if a.list:
        print(json.dumps(catalogue(), indent=1))
        return 0
    if a.tables:
        # Session 182's landing: a finding that says DATA_MACHINE_ONLY reads histories the Roundup's runner should not
        # restore each Sunday (the three cards of session 182 would add about 500 MB: the zone histories, CAISO's
        # curtailment by interval and its supply history). It is computed on the data machine, and its card and
        # downloads are in git; on the runner it is "not computed, a table is missing", named, as any finding is.
        names = sorted({t for m in load_all() if not getattr(m, "DATA_MACHINE_ONLY", False) for t in m.TABLES})
        print("^(" + "|".join(names) + ")$")
        return 0
    if not a.name:
        ap.error("a finding's name, --list or --tables")
    params = {}
    for kv in a.param:
        k, _, v = kv.partition("=")
        params[k] = v
    try:
        run(a.name, params, a.in_dir, a.out_dir, a.out_dir)
    except common.NoData as exc:
        print(f"{a.name}: not computed, a table is missing: {exc}", file=sys.stderr)
        return 3
    except ValueError as exc:
        print(f"{a.name}: {exc}", file=sys.stderr)
        return 2
    except Exception:
        print(f"{a.name} FAILED:\n{traceback.format_exc()}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
