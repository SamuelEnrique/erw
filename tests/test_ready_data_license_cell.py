"""wip/ready-data-license-cell (session 11406, chain 770, part C): the other choice of the data pages audit of
26 November, finding 4 (docs/reviews/data-model-audit-2026-11-26.md), readied for Samuel's ruling, not requested.

On main a /data row's cells can disagree: License "public" beside "Not public (unsettled)" (4 tables whose publishers'
terms the record has not settled); "license needed" beside "Not public (unsettled)" (the held tables); Tier "derived"
with no "(derived)" mark (3 tables). On this branch the License cell takes the record's word where the record holds the
table not public, a held row's tools cell says "Not public (license needed)", and the mark follows the tier as well.
Counted on today's coverage.csv, license record and verdicts (the audit's test, tests/test_audit_data_7.py on
wip/audit-data-7, carried), printed by this test: the License cells, the tools labels and the marks that move."""
import csv
import datetime as dt
import json
import os
import re
import unittest

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def listed():
    with open(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), encoding="utf-8", newline="") as f:
        cov = {r["table"]: r for r in csv.DictReader(f)}
    live = yaml.safe_load(src("warehouse", "supabase", "live_set.yaml"))
    rules = live["full"] + live["recent"]["tables"]
    loaded = lambda t: any(re.match(p, t) for p in rules)  # noqa: E731
    return {t: r for t, r in cov.items() if r["license"] == "public" and t not in set(live["catalogue_hold"])
            and not (loaded(t) and t in set(live["review_hold"]))}


class OneRowOneAnswer(unittest.TestCase):
    def test_the_page(self):
        page = src("site", "app", "data", "page.tsx")
        self.assertIn(') : verdictOf(r.table_name) && verdictOf(r.table_name) !== "public" ? (', page)
        self.assertIn("<span title={refusal(r.table_name) ?? undefined}>{verdictOf(r.table_name)}</span>", page)
        self.assertIn("Not public ({licenseNeeded(r.table_name) ? LICENSE_NEEDED : verdictOf(r.table_name)})", page)
        self.assertIn('{r.derived === "yes" || r.tier === "derived" ? <span className="ml-1 font-sans text-muted">(derived)</span> : null}', page)

    def test_how_many_move(self):
        today = dt.datetime.now(dt.timezone.utc).date().isoformat()
        rows = listed()
        verd = json.loads(src("site", "data", "table_verdicts.json"))
        st = json.loads(src("site", "data", "license_status.json"))["tables"]
        held = {t for t, r in st.items() if r["status"] == "license needed" and today >= r["from"]}
        license_cells = sorted(t for t in rows if t not in held and verd.get(t, ["public"])[0] != "public")
        tool_labels = sorted(t for t in rows if t in held and verd.get(t, ["public"])[0] != "public")
        marks = sorted(t for t, r in rows.items() if r["tier"] == "derived" and r["derived"] != "yes")
        print(f"License cells from 'public' to the record's word: {len(license_cells)} {license_cells}; "
              f"tools labels to 'license needed': {len(tool_labels)}; marks added: {len(marks)} {marks}")
        self.assertIn("state_large_load_laws", license_cells)


if __name__ == "__main__":
    unittest.main()
