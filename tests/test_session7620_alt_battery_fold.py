"""Session 7620: the other choice of the ruling on the battery page's fold (branch wip/alt-battery-2, not landed). The fold
under the income table ("Each month: days held; the storage nodes' four-hour spread at the 10th percentile, median and
90th; the hub's; the share wider") leaves the page and its rows are kept in the CSV alone, as the owner's ruling of
12 October 2026 moved monthly rows.

What is held to:
  the page draws no fold of the storage nodes' months and no per-month figure of node_basis_summary: the twelve months'
    weighted means stay in the band's sentence, which now points to "Every month, CSV";
  months.csv carries the six figures as columns storage_nodes_<figure> for the ERCOT hub, from the same read
    (lib/nodebasisread.ts) the page uses, with a '#' line naming the table, and blank cells for a month not held;
  the page's band and the CSV take the six figures in the same order (STORAGE_VARS).

No request, no model call."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheFoldIsInTheCsvAlone(unittest.TestCase):
    def setUp(self):
        self.page = src("site", "app", "cost-of-power", "battery", "page.tsx")
        self.route = src("site", "app", "cost-of-power", "battery", "months.csv", "route.ts")
        self.read = src("site", "lib", "nodebasisread.ts")

    def test_the_page_draws_no_fold_of_the_nodes_months(self):
        self.assertNotIn("Each month: days held", self.page)
        self.assertNotIn("nodeMonths.map(", self.page)
        self.assertNotIn("|dam_storage_", self.page)
        self.assertIn('data-node-monthly="csv"', self.page)
        band = self.page[self.page.index('data-node-band="storage"'):self.page.index('data-node-band="none"')]
        self.assertEqual(band.count("<details"), 0)
        self.assertIn("href={monthsHref}", band)

    def test_the_csv_carries_the_six_figures_as_columns(self):
        self.assertIn('import { STORAGE_VARS, storageRows } from "@/lib/nodebasisread";', self.route)
        self.assertIn("storage_nodes_${v}", self.route)
        self.assertIn('x.grid === "ercot" && g.entity === "ercot:HB_HUBAVG" ? await storageRows() : null', self.route)
        self.assertIn("from node_basis_summary (the live set)", self.route)
        self.assertIn("...(nodes ? STORAGE_VARS.map((v) => nodeAt(r.m, v)) : [])", self.route)
        six = re.search(r"STORAGE_VARS = \[(.*?)\] as const", self.read).group(1)
        self.assertEqual([s.strip().strip('"') for s in six.split(",")],
                         ["spread_4h_p10", "spread_4h_p50", "spread_4h_p90", "hub_spread_4h", "share_wider_pct", "days"])

    def test_no_em_dash(self):
        for t in (self.page, self.route, src("tests", "test_session7620_alt_battery_fold.py")):
            self.assertNotIn(chr(0x2014), t)


if __name__ == "__main__":
    unittest.main()
