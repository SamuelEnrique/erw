"""Session 585: the trader path (docs/reviews/trader-path.md) walked again on a build, and the one fault it fixed.

The fault: the battery page's source line (SourceLine, components/tool/ToolPage.tsx) did not name the two tables whose
figures are drawn under the income table on ERCOT: the awards line (bsa| keys, data/battery_awards_beside.json, its
fleet_table) and the storage nodes' band (series|node_basis_summary|...). The page now adds each whenever it draws it.
Read only: no build, no browser, no request (the build's record is docs/brand/review-585/foot-after.json).
"""

import csv
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
DOC = os.path.join(ROOT, "docs", "reviews", "trader-path.md")
SHOTS = os.path.join(ROOT, "docs", "brand", "review-585")
STEPS = ["01-seller", "02-seller-wind", "03-seller-west", "04-seller-capture", "05-seller-caiso", "06-seller-ppa", "07-battery",
         "08-battery-awards", "09-battery-2h", "10-battery-4h-dayahead", "11-battery-caiso", "12-battery-income", "13-board",
         "14-board-workbench", "15-board-ercot-hubs", "16-board-week"]


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheSourceLine(unittest.TestCase):
    def setUp(self):
        self.page = src("site", "app", "cost-of-power", "battery", "page.tsx")
        m = re.search(r"<SourceLine tables=\{([\s\S]*?)\}\s*note=", self.page)
        self.assertIsNotNone(m)
        self.tables = m.group(1)

    def test_the_line_names_the_awards_table_when_the_awards_line_is_drawn(self):
        self.assertIn("...(beside ? [(awardsData as unknown as { fleet_table: string }).fleet_table] : [])", self.tables)
        self.assertIn("{beside ? (", self.page)  # the awards line is drawn on the same condition

    def test_the_line_names_the_node_table_when_the_node_band_is_drawn(self):
        self.assertIn('...(nodeMonths ? ["node_basis_summary"] : [])', self.tables)
        self.assertIn("{nodeMonths ? (", self.page)

    def test_the_awards_file_names_a_table_of_the_warehouse(self):
        with open(os.path.join(SITE, "data", "battery_awards_beside.json"), encoding="utf-8") as f:
            awards = json.load(f)
        with open(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), encoding="utf-8", newline="") as f:
            tables = {r["table"] for r in csv.DictReader(f)}
        self.assertEqual(awards["fleet_table"], "ercot_storage_dam_awards_monthly")
        self.assertIn(awards["fleet_table"], tables)
        self.assertIn("node_basis_summary", tables)

    def test_the_build_drew_both_on_ercot_and_neither_on_caiso(self):
        with open(os.path.join(SHOTS, "foot-before.json"), encoding="utf-8") as f:
            before = json.load(f)
        with open(os.path.join(SHOTS, "foot-after.json"), encoding="utf-8") as f:
            after = json.load(f)
        for w in ("1280", "390"):
            for t in ("ercot_storage_dam_awards_monthly", "node_basis_summary"):
                self.assertNotIn(t, before[f"battery-ercot_{w}"])
                self.assertIn(t, after[f"battery-ercot_{w}"])
                self.assertNotIn(t, after[f"battery-caiso_{w}"])
            self.assertEqual(before[f"battery-caiso_{w}"], after[f"battery-caiso_{w}"])
            # the rest of the line is as it was
            self.assertEqual(before[f"battery-ercot_{w}"].split("ercot_as_prices")[1], after[f"battery-ercot_{w}"].split("node_basis_summary")[1])
            for name in ("ercot", "caiso"):
                for tag in ("before", "after"):
                    self.assertTrue(os.path.exists(os.path.join(SHOTS, f"foot-battery-{name}_{tag}_{w}.png")))


class TheWalk(unittest.TestCase):
    def test_every_step_was_shot_and_recorded_at_both_widths(self):
        for w in ("1280", "390"):
            with open(os.path.join(SHOTS, f"walk-{w}.json"), encoding="utf-8") as f:
                rec = json.load(f)
            self.assertEqual([s["step"] for s in rec["steps"]], STEPS)
            for s in rec["steps"]:
                self.assertTrue(s.get("found"), s["step"])
                self.assertNotIn("error", s, s["step"])
                self.assertTrue(os.path.exists(os.path.join(SHOTS, f"{s['step']}_{w}.png")), s["step"])
        with open(os.path.join(SHOTS, "walk-1280.json"), encoding="utf-8") as f:
            links = json.load(f)["links"]
        self.assertEqual(len(links), 139)
        self.assertEqual([l for l in links if l[1] != 200], [])

    def test_the_review_holds_the_dated_section(self):
        doc = src("docs", "reviews", "trader-path.md")
        self.assertIn("## Walked again on a build, 22 October 2026 (session 585)", doc)
        section = doc.split("## Walked again on a build, 22 October 2026 (session 585)")[1].split("## The On.Energy walkthrough")[0]
        for n in range(1, 17):
            self.assertIn(f"\n| {n:02d} |", section)
        self.assertIn("iso_trader_daily", section)
        self.assertNotIn(chr(0x2014), doc)


if __name__ == "__main__":
    unittest.main()
