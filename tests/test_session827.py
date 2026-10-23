"""Session 827: the datacenter tracker's power side, the same sort (chain 080). The sort on an entities table with its
id columns, the committed file, the page's line. No request."""

import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "deals"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import public_rows as P  # noqa: E402
from test_session822 import REGISTRY, VERDICTS  # noqa: E402


class EntitiesSortTest(unittest.TestCase):
    def test_id_columns(self):
        projects = [{"entity_id": "datacenter:1", "name": "A"}, {"entity_id": "datacenter:2", "name": "B"}, {"entity_id": "datacenter:3", "name": "C"}]
        evidence = [
            {"facility_id": "datacenter:1", "story_id": "s1", "source": "Reuters", "source_url": "https://www.reuters.com/a", "event_date": "2026-10-01T00:00:00Z"},
            {"facility_id": "datacenter:2", "story_id": "s2", "source": "DOE newsroom", "source_url": "https://www.energy.gov/a", "event_date": "2026-10-01T00:00:00Z"},
            {"facility_id": "datacenter:3", "story_id": "s3", "source": "Electrek", "source_url": "https://electrek.co/a", "event_date": "2026-10-01T00:00:00Z"},
        ]
        s = P.sort_deals(projects, evidence, REGISTRY, VERDICTS, id_col="entity_id", ev_col="facility_id")
        self.assertEqual({k: v["sort"] for k, v in s.items()}, {"datacenter:1": "held", "datacenter:2": "shown", "datacenter:3": "unsettled"})


class CommittedFileTest(unittest.TestCase):
    def test_counts_and_no_held_name(self):
        with open(os.path.join(SITE, "data", "datacenters_public.json"), encoding="utf-8") as f:
            file = json.load(f)
        self.assertEqual(file["counts"]["shown"], len(file["shown"]))
        self.assertEqual(set(file["counts"]), {"shown", "held", "unsettled"})
        for r in file["shown"]:
            self.assertTrue(r["public_evidence"])
            self.assertEqual(set(r), {"entity_id", "name", "state", "county", "city", "mw", "utility", "power_source", "project_status", "planned_year", "public_evidence", "other_publishers"})
        # the held publishers are named with their counts (a publisher's name is not a row's data); no row of theirs is in the file
        self.assertTrue(all(len(x) == 3 for x in file["held_publishers"]))


class PageCodeTest(unittest.TestCase):
    def read(self, *p):
        with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
            return f.read()

    def test_line_on_the_page(self):
        self.assertIn("<DatacentersPublicLine />", self.read("site", "app", "datacenters", "page.tsx"))
        line = self.read("site", "app", "datacenters", "PublicLine.tsx")
        for k in ('DC_COUNT_KEY("held")', 'DC_COUNT_KEY("unsettled")', 'DC_COUNT_KEY("shown")', "license needed"):
            self.assertIn(k, line, k)
        self.assertIn('p[0] === "dcpub"', self.read("site", "scripts", "check-values.mjs"))
        self.assertIn("dcpub|counts|shown", self.read("docs", "methods", "datacenter_facilities.md"))

    def test_no_em_dash(self):
        for p in (("site", "app", "datacenters", "PublicLine.tsx"), ("docs", "methods", "datacenter_facilities.md"), ("warehouse", "deals", "public_rows.py"), ("tests", "test_session827.py")):
            self.assertNotIn(chr(0x2014), self.read(*p), p)


if __name__ == "__main__":
    unittest.main()
