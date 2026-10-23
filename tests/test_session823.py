"""Session 823: the public subset's figures (chain 080).

The tracker's and the comparables' figures over the shown rows only, with the held count beside each; the months
helper of site/lib/dealspublic.ts (the held months hatched); the reader's held counts by month; the keys; the page code.
No request is made.
"""

import json
import os
import re
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "deals"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import public_rows as P  # noqa: E402
from test_session822 import REGISTRY, VERDICTS, fixtures, node  # noqa: E402


class HeldByMonthTest(unittest.TestCase):
    def test_counts_by_month_name_no_row(self):
        deals, evidence = fixtures()
        out = P.site_json(deals, P.sort_deals(deals, evidence, REGISTRY, VERDICTS), os.path.join(ROOT, "warehouse", "deals", "public_rows.py"))
        self.assertEqual(sum(out["held_by_month"].values()), 10)   # 5 held and 5 unsettled
        self.assertTrue(all(re.fullmatch(r"\d{4}-\d{2}", k) for k in out["held_by_month"]))
        # a shown deal's month is not in the held counts unless a held deal shares it
        held_months = {d["event_date"][:7] for d in deals[5:]}
        self.assertEqual(set(out["held_by_month"]), held_months)

    def test_committed_file(self):
        with open(os.path.join(SITE, "data", "deals_public.json"), encoding="utf-8") as f:
            file = json.load(f)
        self.assertEqual(sum(file["held_by_month"].values()), file["counts"]["held"] + file["counts"]["unsettled"])


class LibTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.got = node(
            "const m = await import('./lib/dealspublic.ts');"
            "console.log(JSON.stringify({"
            " ms: m.monthsWithHeld([{month: '2026-09', n: 2}, {month: '2026-10', n: 3}], {'2026-07': 4, '2026-10': 6}),"
            " none: m.monthsWithHeld([], undefined),"
            " only: m.monthsWithHeld([{month: '2026-10', n: 1}], undefined),"
            " tip: m.shownOnlyTip({shown: 16, held: 486, unsettled: 3}), tip1: m.shownOnlyTip({shown: 1, held: 1, unsettled: 0}),"
            " keys: [m.trackerKey('all', 'mw'), m.trackerKey('selection', 'deals'), m.compPubKey('median_mw', 'type', ''), m.compPubKey('deals', 'grid', 'ERCOT')]}));"
        )

    def test_months_with_held(self):
        ms = self.got["ms"]
        self.assertEqual([x["month"] for x in ms], ["2026-07", "2026-08", "2026-09", "2026-10"])
        self.assertEqual([x["n"] for x in ms], [0, 0, 2, 3])
        self.assertEqual([x["held"] for x in ms], [4, 0, 0, 6])
        self.assertEqual(self.got["none"], [])
        self.assertEqual(self.got["only"], [{"month": "2026-10", "n": 1, "held": 0}])

    def test_tip_and_keys(self):
        self.assertIn("16 shown deals only; 489 held or unsettled deals are not counted (license needed)", self.got["tip"])
        self.assertIn("1 shown deal only; 1 held or unsettled deal is not counted", self.got["tip1"])
        self.assertEqual(self.got["keys"], ["dealpub|tracker|all|mw", "dealpub|tracker|selection|deals", "dealpub|comp_median_mw|type|-", "dealpub|comp_deals|grid|ERCOT"])


class FiguresTest(unittest.TestCase):
    """The tracker's counts and the comparables' cells over the fixtures' shown rows, by lib/deals2.ts as the pages and
    the check compute them: nothing of a held row enters."""

    def test_over_shown_rows_only(self):
        deals, evidence = fixtures()
        out = P.site_json(deals, P.sort_deals(deals, evidence, REGISTRY, VERDICTS), os.path.join(ROOT, "warehouse", "deals", "public_rows.py"))
        got = node(
            "const D = await import('./lib/deals2.ts');"
            f"const rows = {json.dumps(out['shown'])};"
            "const deals = D.fold(rows.map(D.toDeal), []); const c = D.counts(deals);"
            "console.log(JSON.stringify({c, cells: D.comparables(deals, 'type').map((x) => [x.value, x.deals, x.withMw, x.medianMw])}));"
        )
        self.assertEqual(got["c"]["deals"], 5)
        self.assertEqual(got["c"]["withMw"], 5)
        self.assertEqual(got["c"]["mw"], 1500)   # 100 + 200 + 300 + 400 + 500; the held deals' 60 to 100 MW never enter
        self.assertEqual(got["c"]["dollars"], 15_000_000)
        self.assertEqual(got["cells"], [["ppa", 5, 5, 300]])


class PageCodeTest(unittest.TestCase):
    def read(self, *p):
        with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
            return f.read()

    def test_views_take_the_public_file(self):
        v2 = self.read("site", "app", "deals", "v2", "view.tsx")
        for s in ("deals_public.json", "publicOnly", "monthsWithHeld(", "deals-held-hatch", 'trackerKey("all", "deals")', 'trackerKey("selection", stat)', "<DealsHeld file={PUBLIC} />"):
            self.assertIn(s, v2, s)
        comp = self.read("site", "app", "deals", "comparables", "view.tsx")
        for s in ("deals_public.json", "publicOnly", "compPubKey", "<DealsHeld file={PUBLIC} />"):
            self.assertIn(s, comp, s)
        cv = self.read("site", "scripts", "check-values.mjs")
        self.assertIn('p[1] === "tracker"', cv)
        self.assertIn("dealpub|tracker|all|<stat>", self.read("docs", "methods", "energy_deals.md"))

    def test_no_em_dash(self):
        for p in (("site", "lib", "dealspublic.ts"), ("site", "app", "deals", "v2", "view.tsx"), ("site", "app", "deals", "comparables", "view.tsx"),
                  ("site", "scripts", "check-values.mjs"), ("docs", "methods", "energy_deals.md"), ("tests", "test_session823.py")):
            self.assertNotIn(chr(0x2014), self.read(*p), p)


if __name__ == "__main__":
    unittest.main()
