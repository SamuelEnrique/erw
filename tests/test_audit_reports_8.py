"""Session 10232, the report library audit (docs/reviews/reports-model-audit-2026-11-26.md), finding 8. Shows the
finding; not for landing (a change would bring figures back to a page: Samuel's ruling on the license, default left as
it is).

ai_power_regions is held by grid for ISO-NE, MISO and NYISO (site/data/license_status.json), and lib/license.ts holds
a row by the grid its entity names (iso:isone), whatever the measure. So the AI gigawatts draft loses, with those grids'
prices and queues (27 rows), 53 rows that rest on no grid operator's data: EIA-930's carbon and imports, Berkeley Lab's
Queued Up (CC BY 4.0), the event studies. Among them MISO's carbon intensity, 435.82 kg/MWh, the highest of the seven,
which would make MISO, not SPP, the dirtiest region in the draft's second finding.

The data test reads ai_power_regions from ERW_AUDIT_OUTPUT (or warehouse/output) and is skipped where it is not held.
"""
import csv
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.environ.get("ERW_AUDIT_OUTPUT") or os.path.join(ROOT, "warehouse", "output")
GRID = ("flat_rt_price", "flat_da_price", "flat_1gw_cost", "rt_hours_priced", "scarcity_hours", "max_rt_hour", "rt_hours_seen", "queue_active")


class TheHoldTakesEveryMeasureOfAHeldGrid(unittest.TestCase):
    def test_the_table_is_held_by_grid(self):
        with open(os.path.join(ROOT, "site", "data", "license_status.json"), encoding="utf-8") as f:
            row = json.load(f)["tables"]["ai_power_regions"]
        self.assertEqual(row["status"], "license needed")
        self.assertNotEqual(row.get("hold"), "row")

    def test_a_row_is_held_by_its_grid_not_its_measure(self):
        with open(os.path.join(ROOT, "site", "lib", "license.ts"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn("const g = gridOfEntity(entity);", s)
        self.assertIn("return !!g && licensePublishers(table).some((p) => GRID_PREFIX[p] === g);", s)

    def test_the_builder_names_sources_other_than_the_grids(self):
        with open(os.path.join(ROOT, "warehouse", "derived", "ai_power_regions.py"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn("Berkeley Lab and GridTracker (CC BY 4.0", s)
        self.assertIn("carbon_intensity_daily", s)

    @unittest.skipUnless(os.path.exists(os.path.join(OUT, "ai_power_regions.csv")), "ai_power_regions not held here")
    def test_held_rows_from_no_grid_operator(self):
        n = 0
        miso_ci = None
        with open(os.path.join(OUT, "ai_power_regions.csv"), encoding="utf-8") as f:
            for r in csv.DictReader(ln for ln in f if not ln.startswith("#")):
                reg = r["entity"].split(":")[1]
                if reg in ("isone", "miso", "nyiso") and not r["variable"].startswith("event_largest_is_") and not r["variable"].startswith(GRID):
                    n += 1
                if reg == "miso" and r["variable"] == "carbon_intensity_kg_mwh":
                    miso_ci = float(r["value"])
        self.assertGreater(n, 40)
        self.assertIsNotNone(miso_ci)


if __name__ == "__main__":
    unittest.main()
