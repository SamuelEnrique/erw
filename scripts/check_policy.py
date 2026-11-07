#!/usr/bin/env python3
"""Every date and every figure the policy monitor shows, traced to its document's row of policy_actions (session 3061,
chain 166), in the form of scripts/check_digest.py.

Energy Research Warehouse (ERW). The monitor (/policy?view=monitor) reads site/data/policy/monitor.json; each step of
its calendar and each figure of its table carries a key (site/lib/policymonitor.ts: policycal|<record>|<document>|
<kind>|<date> and policyfig|<record>|<document>|<value>|<unit>). This script reads those keys as the site makes them
(site/scripts/policy-figures.mjs, run with node) and finds each in its document's row:

    policycal   the step (kind and date) stands in the row's `dates` (the connector's, warehouse/policy/fields.py), or,
                for a row the table holds without those columns, in what fields.derive reads from the row's own
                summary; and the record holds the document (its proceeding id is the row's, or the record is that
                document's own)
    policyfig   the figure (value and unit) is the row's figure_value and figure_unit, or what derive reads, the same way
    policysum   (session 3062) a chart's sum of MW or USD in a month: every record it names has its figure traced, in
                that unit, and the figures add to the sum

    python scripts/check_policy.py                    # the local CSVs (warehouse/output), read only
    python scripts/check_policy.py --in-dir DIR       # the CSVs of another copy
    python scripts/check_policy.py --keys FILE        # keys already written by policy-figures.mjs
    python scripts/check_policy.py --file FILE        # another monitor.json

Each key is one line: ok, FAIL (the row says otherwise), or "not here" (the copy read does not hold the document, or
holds it without its text's fields and its summary does not state the step: the data machine's copy has them). Exit 1
when any key fails, or when none could be checked; 0 otherwise. Writes nothing.
"""

import argparse
import json
import os
import subprocess
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "policy"))
import policy_fields as pf  # noqa: E402  session 3233: its own name, beside the deals tracker's fields
import records as pr  # noqa: E402

SITE = os.path.join(ROOT, "site")
FILE = os.path.join(SITE, "data", "policy", "monitor.json")


def keys_from_site(file=FILE):
    """The keys as the page makes them (node and site/scripts/policy-figures.mjs)."""
    r = subprocess.run(["node", "--import", "./scripts/alias-register.mjs", "scripts/policy-figures.mjs", os.path.abspath(file)],
                       cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=300)
    if r.returncode != 0:
        raise RuntimeError(f"policy-figures.mjs exit {r.returncode}: {(r.stderr or r.stdout).strip()[-300:]}")
    line = [ln for ln in r.stdout.splitlines() if ln.startswith("{")][-1]
    return json.loads(line)


def read_actions(in_dir):
    path = os.path.join(in_dir, "policy_actions.csv")
    with open(path, encoding="utf-8") as f:
        skip = sum(1 for ln in f if ln.startswith("#"))
    a = pd.read_csv(path, skiprows=skip, dtype=str, keep_default_na=False)
    return {r["event_id"]: r for r in a.to_dict("records")}


def fields_of(row):
    """The row's fields: the connector's columns where it wrote them, else what derive reads from the row's summary."""
    if row.get("fields_from"):
        return row, "the table's columns"
    return pf.derive(row, "", None), "derived from the row's summary"


def check(k, rows):
    """("ok" | "FAIL" | "not here", why) for one key."""
    row = rows.get(k["event_id"])
    if row is None:
        return "not here", f"{k['event_id']} is not in this copy of policy_actions"
    body = row.get("body") or pf.body(row.get("agency", ""), None, row.get("docket", ""), row.get("title", ""))
    ids = pr.proceeding_ids(row.get("docket", ""), body)
    if not (k["record"] == f"doc:{k['event_id']}" or k["record"] in ids or k["record"].startswith("doc:")):
        return "FAIL", f"the record {k['record']} is not a proceeding of {k['event_id']} ({';'.join(ids) or 'none named'})"
    f, how = fields_of(row)
    if k["kind"] == "figure":
        if not f.get("figure_value"):
            return ("not here", f"no figure in {how}") if how != "the table's columns" else ("FAIL", f"the row holds no figure ({how})")
        same = abs(float(f["figure_value"]) - float(k["value"])) < 1e-9 and f["figure_unit"] == k["unit"]
        return ("ok", how) if same else ("FAIL", f"the row says {f['figure_value']} {f['figure_unit']} ({how})")
    pair = f"{k['kind']}={k['date']}"
    have = [p for p in (f.get("dates") or "").split("; ") if p]
    if pair in have:
        return "ok", how
    if how != "the table's columns":
        return "not here", f"{pair} is not in what the row's summary states; the row's text is not on this machine"
    return "FAIL", f"{pair} is not in the row's dates ({'; '.join(have) or 'none'})"


def check_sum(k, figures):
    """A sum of the charts (policysum|<unit>|<month>|<value>|<n>): every record it names has its figure traced, in the
    sum's unit, and the figures add to the sum."""
    recs = [r for r in k["record"].split(";") if r]
    missing = [r for r in recs if r not in figures]
    if missing:
        return "FAIL", f"records with no figure key: {missing[:3]}"
    bad = [r for r in recs if figures[r][0] == "FAIL" or figures[r][2] != k["unit"]]
    if bad:
        return "FAIL", f"records whose figure fails or is in another unit: {bad[:3]}"
    total = sum(figures[r][1] for r in recs)
    if abs(total - float(k["value"])) > 1e-6 * max(1.0, abs(total)):
        return "FAIL", f"the {len(recs)} figures add to {total:g}, not {k['value']}"
    if any(figures[r][0] == "not here" for r in recs):
        return "not here", "a figure of the sum is not traced on this copy"
    return "ok", f"{len(recs)} figures, each traced"


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: trace the policy monitor's dates and figures (session 3061)")
    ap.add_argument("--in-dir", default=os.path.join(ROOT, "warehouse", "output"))
    ap.add_argument("--keys", help="the JSON policy-figures.mjs printed")
    ap.add_argument("--file", default=FILE)
    args = ap.parse_args(argv)
    if args.keys:
        with open(args.keys, encoding="utf-8") as f:
            got = json.load(f)
    else:
        got = keys_from_site(args.file)
    rows = read_actions(args.in_dir)
    n = {"ok": 0, "FAIL": 0, "not here": 0}
    figures = {}   # record: (verdict, value, unit) of its figure, for the sums
    for k in got["keys"]:
        if k["kind"] == "sum":
            continue
        verdict, why = check(k, rows)
        if k["kind"] == "figure":
            figures[k["record"]] = (verdict, float(k["value"]), k["unit"])
        n[verdict] += 1
        print(f"{verdict:8s} {k['key']}  {why}")
    for k in got["keys"]:   # session 3062: a chart's sum is its records' figures, each traced, added
        if k["kind"] != "sum":
            continue
        verdict, why = check_sum(k, figures)
        n[verdict] += 1
        print(f"{verdict:8s} {k['key']}  {why}")
    print(f"check_policy: {len(got['keys'])} keys of monitor.json (built {got['built']}, {got['records']} records): "
          f"{n['ok']} ok, {n['FAIL']} FAIL, {n['not here']} not here")
    return 1 if n["FAIL"] or n["ok"] == 0 else 0


if __name__ == "__main__":
    sys.exit(main())
