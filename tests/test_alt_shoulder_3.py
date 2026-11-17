"""Ruling alternative 3 of /shoulder (session 7703, 17 November 2026, branch wip/alt-shoulder-3; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-shoulder-2026-11-17.md, line 3): which demand
California's net load stands on, EIA-930's (counts the batteries' charging) or CAISO's own (does not)? Main sets both side
by side for June to November 2025. On this branch one source is the measure in any month: CAISO's own data for every
month it holds, EIA-930 for the months before (site/lib/shoulder.ts oneSource); a month of EIA-930 that CAISO's own data
measures opens on CAISO's own data, and the side-by-side section is gone.

Pinned with the page's own code drawn on the table (site/scripts/alt-shoulder-draw.mjs), where shoulder_hours_monthly is
on the machine (warehouse/output, or the folder ERW_TABLES_DIR names): California asked for June 2025 reads 60,760 MWh
above the mean (EIA-930: 47,397, +28.2 percent); August 66,294 (51,772, +28.1 percent), hours needed 4.65 (3.63); October
58,868 (41,416, +42.1 percent); November 50,369 (36,217, +39.1 percent), hours needed 3.31 (2.38). EIA-930 opens on May
2025, its last month before CAISO's own data.

    python -m unittest tests.test_alt_shoulder_3 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
CSV = os.path.join(TABLES, "shoulder_hours_monthly.csv")
K = "series|shoulder_hours_monthly|{}|{}|{}-01T00:00:00Z"


def draw(path, queries):
    p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-shoulder-draw.mjs", path, json.dumps(queries)],
                       cwd=SITE, capture_output=True, text=True, timeout=600)
    if p.returncode != 0:
        raise AssertionError(p.stderr[-2000:])
    return json.loads(p.stdout)


@unittest.skipUnless(os.path.exists(CSV), "shoulder_hours_monthly is not on this machine")
class OnTheTable(unittest.TestCase):
    MONTHS = {"2025-06": (60760, None), "2025-08": (66294, 4.65), "2025-10": (58868, 3.92), "2025-11": (50369, 3.31)}

    @classmethod
    def setUpClass(cls):
        cls.d = draw(CSV, [{"grid": "caiso", "month": m} for m in cls.MONTHS] + [{"grid": "caiso"}])

    def test_each_month_asked_of_eia930_is_measured_on_caisos_own_data(self):
        for d, (m, (mwh, needed)) in zip(self.d, self.MONTHS.items()):
            c = d["checks"]
            self.assertEqual(round(c[K.format("iso:caiso_own", "shoulder_mwh_above_mean", m)]), mwh, m)
            self.assertNotIn(K.format("iso:caiso", "shoulder_mwh_above_mean", m), c, m)
            self.assertIn("one-source=moved", d["marks"], m)
            if needed is not None:
                self.assertIn(f"they would need {needed:.2f} hours on the average day", d["summary"], m)

    def test_eia930_opens_on_its_last_month_before_caisos_own(self):
        d = self.d[-1]
        self.assertTrue(d["summary"].startswith("In May 2025, by EIA-930, CAISO's evening shoulder"), d["summary"][:80])
        self.assertIn("one-source=eia930", d["marks"])
        self.assertNotIn("California's two sources, side by side", d["text"])


if __name__ == "__main__":
    unittest.main()
