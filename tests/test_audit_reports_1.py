"""Session 10232, the report library audit (docs/reviews/reports-model-audit-2026-11-26.md), finding 1.

From 21 October 2026 ai_power_regions is "license needed" for ISO-NE, MISO and NYISO (site/data/license_status.json),
held by grid, so the live-set read of /reports/draft/ai-gigawatts leaves out those three regions' rows. The draft went on
saying "seven U.S. ISO regions", printed "not held" in their cells (the warehouse holds them; a license holds them back)
and drew its five findings, rankings and tally from four regions, cost from three. The fix is words only: the held
regions are named in one line, as the shape-premium draft names its held hubs (session 383), and their cells say
"license needed". No figure moves.
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PAGE = os.path.join(ROOT, "site", "app", "reports", "draft", "ai-gigawatts", "page.tsx")
STATUS = os.path.join(ROOT, "site", "data", "license_status.json")


def src():
    with open(PAGE, encoding="utf-8") as f:
        return f.read()


class TheHeldRegionsAreNamed(unittest.TestCase):
    def test_the_table_is_held_for_three_grids(self):
        with open(STATUS, encoding="utf-8") as f:
            row = json.load(f)["tables"]["ai_power_regions"]
        self.assertEqual(row["status"], "license needed")
        self.assertEqual(sorted(row["publishers"]), ["ISO-NE", "MISO", "NYISO"])

    def test_the_page_splits_the_regions_by_the_hold(self):
        s = src()
        self.assertIn('import { LICENSE_NEEDED, licenseHeldRow } from "@/lib/license";', s)
        self.assertIn("const HELD = REGIONS.filter((g) => licenseHeldRow(T, `iso:${g.id}`));", s)

    def test_the_held_regions_are_named_once_at_the_top(self):
        s = src()
        self.assertIn("data-held-regions", s)
        self.assertIn("{LICENSE_NEEDED} (held from 21 October 2026, lib/license.ts)", s)
        self.assertIn("Where the\n          words below say seven", s)

    def test_held_cells_say_license_needed_not_not_held(self):
        s = src()
        self.assertIn("{R.map((r) => isHeld(r.id) ? (", s)
        self.assertIn('<td colSpan={5} className="py-1 pr-3 text-right text-muted">{LICENSE_NEEDED}</td>', s)
        self.assertIn("{isHeld(t.r.id) ? <td colSpan={2}", s)

    def test_no_sentence_about_isone_while_isone_is_held(self):
        s = src()
        self.assertIn('{isHeld("isone") ? null : <> ISO-NE has no median here', s)
        self.assertIn("""{isHeld("isone") ? "" : ", ISO-NE's time to connect"}""", s)

    def test_no_em_dash(self):
        self.assertNotIn(chr(0x2014), src())
        with open(__file__, encoding="utf-8") as f:
            self.assertNotIn(chr(0x2014), f.read())


if __name__ == "__main__":
    unittest.main()
