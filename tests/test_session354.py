"""Session 354 (the chain of 20 October 2026, night): /cost-of-power. ERCOT's four summer peaks against the flexible
way's own hours (ercot_4cp_intervals), counted in scenario A and B only when the reader asks (`cp=1`); the band of a
node's day-ahead basis to the hub (node_basis_summary); capacity charges, from a public table only, "no public figure"
otherwise. Every default figure is what it was. Energy Research Warehouse (ERW)."""
import os
import unittest
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DASH = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheFourPeaks(unittest.TestCase):
    def setUp(self):
        self.model = src("site", "app", "cost-of-power", "model.ts")

    def test_an_interval_is_its_hour_of_the_standard_time_year(self):
        # the page's rule, in Python: the hour of the year in the grid's standard time (UTC-6 for ERCOT)
        self.assertIn("const t = Date.parse(r.ts_utc) - behind * 3600000, y = new Date(t).getUTCFullYear();", self.model)
        self.assertIn("const i = Math.floor((t - Date.UTC(y, 0, 1)) / 3600000);", self.model)
        ts = datetime(2025, 8, 18, 21, 45, tzinfo=timezone.utc).timestamp() * 1000 - 6 * 3600000
        start = datetime(2025, 1, 1, tzinfo=timezone.utc).timestamp() * 1000
        self.assertEqual(int((ts - start) // 3600000), (31 + 28 + 31 + 30 + 31 + 30 + 31 + 17) * 24 + 15)   # 18 August, 15:00 to 16:00 Central standard time

    def test_the_saving_is_counted_only_when_asked(self):
        self.assertIn("avoided: iv.length === 4 && iv.every((k) => k.w !== null) ? 1 - iv.reduce((a, k) => a + k.w!, 0) / 4 : null", self.model)
        self.assertIn('r.quantity === "postage_stamp_rate" && r.status === "approved" && r.matrix !== "B"', self.model)
        self.assertIn('cp = { summers, rate, newest, perMw, on: q.cp === "1" && perMw !== null };', self.model)
        self.assertIn("if (cp.on && ways[1]) ways = [ways[0], { ...ways[1], cost: ways[1].cost - perMw!, per: (ways[1].cost - perMw!) / ways[1].energy }];", self.model)
        page = src("site", "app", "cost-of-power", "page.tsx")
        self.assertIn('<ParamChoice name="cp" value={M.cp.on ? "1" : ""} dflt="" label="Four summer peaks"', page)
        self.assertIn("check={`series|ercot_4cp_intervals|ercot:system|cp4_load_mw|${iv.ts}`}", page)


class TheNodeAndCapacity(unittest.TestCase):
    def test_the_band_and_the_row(self):
        model = src("site", "app", "cost-of-power", "model.ts")
        self.assertIn('const vars = ["p10", "p50", "p90"].map((k) => `dam_all_basis_${k}`);', model)
        page = src("site", "app", "cost-of-power", "page.tsx")
        self.assertIn("Not added to any figure.", page)
        self.assertIn('{ key: "capacity", cells: ["Capacity charges"], wide: x.grid === "ercot"', page)
        self.assertIn('<Missing words="no public figure" why={CAPACITY_WHY[x.grid]', page)
        for grid in ("nyiso", "isone", "caiso", "spp"):
            self.assertIn(f"  {grid}: \"", page)

    def test_no_em_dash(self):
        for parts in (("site", "app", "cost-of-power", "model.ts"), ("site", "app", "cost-of-power", "page.tsx"), ("tests", "test_session354.py")):
            self.assertNotIn(DASH, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
