"""ERW: the page file of "Energy per AI query, as published" (site/data/ai_energy.json).

Session 8012, chain 505 (part B2). The table ai_energy_published (warehouse/connectors/ai_energy_published.py; method
docs/methods/ai_energy_published.md) holds each figure a model maker, a cloud operator or a peer-reviewed paper printed
for the energy of a query, a token, a training run or a fleet: one row a printed figure, with the publication's own
words. The site is deployed from git and warehouse/output is not in git, so the page reads this file: the table's rows
as they stand, nothing computed, averaged, summed or ranked, and the table's provenance lines with them.

    python warehouse/derived/ai_energy_page.py [--table PATH] [--out PATH]

Run after the connector, whenever its rows change (they change only when a session reads a publication).
"""
import argparse
import csv
import datetime as dt
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TABLE = os.path.join(ROOT, "warehouse", "output", "ai_energy_published.csv")
OUT = os.path.join(ROOT, "site", "data", "ai_energy.json")
FIELDS = ["event_id", "event_date", "parties", "source_url", "x_publisher_kind", "x_peer_reviewed", "x_title", "x_authors", "x_page",
          "x_printed", "x_value", "x_unit", "x_measures", "x_subject", "x_period", "x_basis", "x_sha256", "x_retrieved_at"]


def read(path):
    with open(path, encoding="utf-8", newline="") as f:
        lines = f.read().splitlines()
    head = [ln[1:].strip() for ln in lines if ln.startswith("#")]
    rows = list(csv.DictReader(ln for ln in lines if not ln.startswith("#")))
    return head, rows


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", default=TABLE)
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args(argv)
    if not os.path.exists(a.table):
        raise SystemExit(f"no table at {a.table}: run warehouse/connectors/ai_energy_published.py first")
    head, rows = read(a.table)
    if not rows:
        raise SystemExit("the table holds no row")
    missing = [k for k in FIELDS if k not in rows[0]]
    if missing:
        raise SystemExit(f"the table lacks {missing}")
    lic = next((h.split(":", 1)[1].strip() for h in head if h.startswith("License:")), "")
    out = []
    for r in rows:
        x = {k: r[k] for k in FIELDS}
        x["x_value"] = float(r["x_value"]) if r["x_value"] not in ("", None) else None
        out.append(x)
    doc = {"built": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "table": "ai_energy_published",
           "method": "docs/methods/ai_energy_published.md", "license": lic, "provenance": head, "rows": out}
    text = json.dumps(doc, ensure_ascii=False, indent=1)
    if chr(0x2014) in text:
        raise SystemExit("an em dash in the rows: the repository allows none")
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write(text + "\n")
    print(f"{a.out}: {len(out)} figures from {len({r['x_title'] for r in out})} publications")
    return 0


if __name__ == "__main__":
    sys.exit(main())
