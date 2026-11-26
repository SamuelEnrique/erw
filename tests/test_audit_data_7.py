"""Audit of the data pages, finding 4, for Samuel's ruling (session 10233, docs/reviews/data-model-audit-2026-11-26.md).
A test only, not for landing: it shows what /data's cells of one row say against each other, and changes nothing.

/data's catalogue (coverage.csv less the live set's catalogue_hold, less what review_hold loads) draws each row's License
cell from coverage and the hold (site/lib/license.ts), its tools cell from the packages' verdicts (site/data/
table_verdicts.json, site/lib/packages.ts refusal), and its "(derived)" mark from coverage's derived flag while the Tier
cell is coverage's tier. On 26 November:
- 4 listed tables print License "public" and "Not public (unsettled)": their verdict says their publishers' terms have
  not been read or settled, and version 1's list leaves them out (state_large_load_laws and three utility large-load
  tables);
- the 32 listed held tables print "license needed" beside "Not public (unsettled)", while the verdict's own words say the
  terms ask for written permission;
- 3 listed tables print Tier "derived" without the "(derived)" mark.

The other choice, not made (a table's listed license or status): the License cell drawn from the verdict where it is
not public, the held rows' tools cell worded "license needed", the mark drawn from the tier. Default: left as it is."""
import csv
import json
import os
import re
import unittest

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TODAY = "2026-11-26"


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def listed():
    with open(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), encoding="utf-8", newline="") as f:
        cov = {r["table"]: r for r in csv.DictReader(f)}
    live = yaml.safe_load(src("warehouse", "supabase", "live_set.yaml"))
    rules = live["full"] + live["recent"]["tables"]
    loaded = lambda t: any(re.match(p, t) for p in rules)
    return {t: r for t, r in cov.items() if r["license"] == "public" and t not in set(live["catalogue_hold"])
            and not (loaded(t) and t in set(live["review_hold"]))}


class ARowsCellsDisagree(unittest.TestCase):
    def setUp(self):
        self.rows = listed()
        self.verd = json.loads(src("site", "data", "table_verdicts.json"))
        st = json.loads(src("site", "data", "license_status.json"))["tables"]
        self.held = {t for t, r in st.items() if r["status"] == "license needed" and TODAY >= r["from"]}

    def test_public_in_the_license_cell_and_not_public_in_the_tools_cell(self):
        both = sorted(t for t in self.rows if t not in self.held and self.verd.get(t, ["public"])[0] != "public")
        self.assertGreater(len(both), 0)
        self.assertIn("state_large_load_laws", both)
        with open(os.path.join(ROOT, "docs", "redivis", "release-v1", "tables.csv"), encoding="utf-8", newline="") as f:
            rel = {r["table"]: r["in_v1"] for r in csv.DictReader(f)}
        for t in both:
            self.assertEqual(self.rows[t]["license"], "public")
            self.assertEqual(rel.get(t), "no", t)
        print(f"\nlisted as public, verdict not public: {len(both)} {both}")

    def test_license_needed_beside_unsettled(self):
        held_listed = sorted(t for t in self.rows if t in self.held)
        words = [self.verd[t][0] for t in held_listed]
        self.assertTrue(held_listed)
        self.assertEqual(set(words), {"unsettled"})
        self.assertTrue(all("ask for written permission" in self.verd[t][1] or "license" in self.verd[t][1] for t in held_listed))
        print(f"\nheld rows whose tools cell says unsettled: {len(held_listed)}")

    def test_tier_derived_without_the_mark(self):
        page = src("site", "app", "data", "page.tsx")
        self.assertIn('r.derived === "yes" ? <span className="ml-1 font-sans text-muted">(derived)</span>', page)
        unmarked = sorted(t for t, r in self.rows.items() if r["tier"] == "derived" and r["derived"] != "yes")
        self.assertTrue(unmarked)
        print(f"\ntier derived, no mark: {len(unmarked)} {unmarked}")


if __name__ == "__main__":
    unittest.main()
