#!/usr/bin/env python3
"""Energy per AI query, as published: every figure a model maker, a cloud operator or a peer-reviewed paper has printed
for the energy of a query, a token, a training run or a fleet, each with its printed words, page and date (session 8005,
chain 501 step D3).

Energy Research Warehouse (ERW) connector. One events table, warehouse/output/ai_energy_published.csv, from the rows a
session wrote by reading each publication itself (warehouse/sources/ai_energy_published/rows.csv). No script calls a
model. Method: docs/methods/ai_energy_published.md.

    python warehouse/connectors/ai_energy_published.py                 # the table (data lock)
    python warehouse/connectors/ai_energy_published.py --out-dir DIR   # a trial

THE RULE. Each row's `printed` is the publication's own words, cut from its saved copy
(warehouse/raw/ai_energy_published/<run>/, each file with its sha256 in manifest.csv). The build refuses a row whose
printed words are not in the saved text of its publication (spaces aside, since a PDF's text comes out without some of
them; "[...]" marks a cut where a page break or a footnote falls between two pieces, each of which must be there). The
value is the number in the printed words, in the publication's own unit; nothing is converted, summed or averaged across
publishers, and the ERW adds no figure of its own (docs/accelerator/large_load_pilot.md). A publisher read that printed
no energy figure (Mistral AI's life-cycle note of July 2025 prints emissions, water and resource figures only) has no
row; the method note lists it.

THE TABLE (events, event_type publication). event_id ai_energy:<id>; event_date the publication's date as its page gives
it; parties the publisher; source the publication's address; x_publisher_kind, x_peer_reviewed, x_title, x_authors,
x_page, x_printed, x_value, x_unit, x_measures, x_subject, x_period, x_basis, x_saved_as, x_sha256.
"""

import argparse
import csv
import datetime as dt
import glob
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

NAME = "ai_energy_published"
SOURCE = "erw:ai_energy_published"
ROWS = os.path.join(ROOT, "warehouse", "sources", "ai_energy_published", "rows.csv")
RAW = os.path.join(ROOT, "warehouse", "raw", "ai_energy_published")
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ai_energy_published.md"
COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source", "source_url",
        "x_publisher_kind", "x_peer_reviewed", "x_title", "x_authors", "x_page", "x_printed", "x_value", "x_unit", "x_measures",
        "x_subject", "x_period", "x_basis", "x_saved_as", "x_sha256", "x_retrieved_at"]


def squash(s):
    return re.sub(r"\s+", "", s).replace("−", "-").replace("×", "x")


def check(printed, text):
    t = squash(re.sub(r"-[ \t]*\n", "", text))   # a word broken across two lines by a hyphen is read whole
    return all(squash(p) in t for p in printed.split("[...]") if p.strip())


def number_in(printed, value):
    nums = [float(x.replace(",", "")) for x in re.findall(r"\d[\d,]*\.?\d*", printed.replace("10−4", "").replace("10-4", ""))]
    return any(abs(n - value) < 1e-9 * max(1.0, abs(value)) for n in nums) or "×" in printed or "x10" in printed


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir")
    a = ap.parse_args(argv)
    runs = sorted(glob.glob(os.path.join(RAW, "*", "manifest.csv")))
    if not runs:
        raise SystemExit(f"no saved publications under {RAW}")
    man = {}
    for m in runs:
        with open(m, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["status"] == "200":
                    man[r["id"]] = dict(r, dir=os.path.dirname(m))
    rows = list(csv.DictReader(open(ROWS, encoding="utf-8")))
    out, bad = [], []
    for r in rows:
        sid = r["saved_as"].rsplit(".", 1)[0]
        m = man.get(sid)
        if not m:
            bad.append(f"{r['id']}: no saved copy {sid}")
            continue
        text = open(os.path.join(m["dir"], sid + ".txt"), encoding="utf-8").read()
        if not check(r["printed"], text):
            bad.append(f"{r['id']}: the printed words are not in {sid}: {r['printed']!r}")
            continue
        v = float(r["value"])
        if not number_in(r["printed"], v):
            bad.append(f"{r['id']}: the value {v} is not a number of the printed words")
            continue
        out.append({"event_id": f"ai_energy:{r['id']}", "event_date": r["date"], "event_type": "publication", "parties": r["publisher"],
                    "entity_ids": "", "mw": "", "price": "", "currency": "", "status": "published", "source": SOURCE, "source_url": r["url"],
                    "x_publisher_kind": r["publisher_kind"], "x_peer_reviewed": r["peer_reviewed"], "x_title": r["title"],
                    "x_authors": r["authors"], "x_page": r["page"], "x_printed": r["printed"], "x_value": v, "x_unit": r["unit"],
                    "x_measures": r["measures"], "x_subject": r["subject"], "x_period": r["period"], "x_basis": r["basis"],
                    "x_saved_as": os.path.relpath(os.path.join(m["dir"], m["saved_as"]), ROOT).replace(os.sep, "/"),
                    "x_sha256": m["sha256"], "x_retrieved_at": m["retrieved_utc"]})
    if bad:
        raise SystemExit("refused, nothing written:\n  " + "\n  ".join(bad))
    t = pd.DataFrame(out)[COLS].sort_values(["event_date", "event_id"]).reset_index(drop=True)
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_dir = os.path.join(a.out_dir, "logs") if a.out_dir else ip.LOG_DIR
    os.makedirs(log_dir, exist_ok=True)
    log = ip.Log(os.path.join(log_dir, f"ai_energy_published_{run_id}.log"))
    pubs = sorted(set(t["source_url"]))
    ip.write_snapshot(t, NAME, [
        "Energy Research Warehouse (ERW): energy per AI query, as published: each figure a model maker, a cloud operator or a peer-reviewed paper printed for the energy of a query, a token, a training run or a fleet (session 8005, chain 501)",
        "Shape: events (docs/datastandard.md v0), event_type publication. One row a printed figure: x_printed the publication's own words, cut from its saved copy; x_value the number in them, in x_unit; x_measures what it measures; x_subject what it is of; "
        "x_page; event_date the publication's date. Nothing is converted, summed or averaged across publishers; the ERW adds no figure of its own. Method: docs/methods/ai_energy_published.md.",
        f"Rows written by a session reading each publication itself (warehouse/sources/ai_energy_published/rows.csv); no model is called. {len(t)} figures from {len(pubs)} publications.",
        f"Retrieved: the publications {min(t['x_retrieved_at'])} to {max(t['x_retrieved_at'])}; built {run_id} (UTC) by warehouse/connectors/ai_energy_published.py",
        f"Run log: warehouse/output/logs/ai_energy_published_{run_id}.log",
        "Source: " + SOURCE + " the publications named per row (source_url), saved at warehouse/raw/ai_energy_published/ with their sha256: " + "; ".join(pubs),
        "License: public (short quotations of published figures with their sources, and the ERW's own reading of them; each publication remains its publisher's)",
    ], log, COLS)
    ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), from published figures",
                            report="Energy per AI query, as published (docs/methods/ai_energy_published.md)", report_url=METHOD_URL,
                            document_list="warehouse/sources/ai_energy_published/rows.csv", license="public", tables=[NAME])])
    log.close()
    print(f"{NAME}: {len(t)} rows from {len(pubs)} publications")
    return 0


if __name__ == "__main__":
    sys.exit(main())
