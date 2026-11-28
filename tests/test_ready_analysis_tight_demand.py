"""wip/ready-analysis-tight-demand (session 11406, chain 770, part C): the other choice of the Automated Analysis
audit of 26 November, finding 3 (docs/reviews/analysis-model-audit-2026-11-26.md), readied for Samuel's ruling, not
requested.

On main grid_stress_yearly's tightest hours (warehouse/derived/mix_stress.py) are the 100 hours of highest net load, so
as a grid adds solar they move to hours with no sun and solar's share in them falls by construction: on a grid whose
demand and sun never change, 43.5 percent of capacity at a capacity of 5 percent of the peak, 3.2 at 60. On this branch
they are the 100 hours of highest demand (tight_hours): 55.6 percent whatever the capacity. The table's own figures
(ERCOT's solar 71.1 percent in 2019 against 5.0 in 2025, draft 3) move when it is rebuilt from EIA-930's hourly rows on
the data machine (the audit's data request 2; the hourly rows are not on this machine). The audit's synthetic grid
(tests/test_audit_analysis_3.py on wip/audit-analysis-3) is carried and run through the builder's own tight_hours."""
import math
import os
import sys
import unittest

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))


def year():
    h = np.arange(8760)
    hour, day = h % 24, h // 24
    season = 0.5 - 0.5 * np.cos(2 * math.pi * (day - 15) / 365)
    demand = 0.62 + 0.18 * season + (0.10 + 0.10 * season) * np.exp(-((hour - 16.0) ** 2) / 18.0)
    sun = np.clip(np.cos(math.pi * (hour - 13.0) / 13.0), 0, None) ** 2 * (0.75 + 0.25 * season)
    sun[(hour < 7) | (hour > 19)] = 0.0
    return demand / demand.max(), sun


class TightHoursByDemand(unittest.TestCase):
    def test_the_builder_chooses_by_demand(self):
        try:
            import mix_stress
        except Exception as exc:
            self.skipTest(f"mix_stress does not import here: {exc}")
        self.assertEqual((mix_stress.TIGHT, mix_stress.TIGHT_BY), (100, "demand"))
        demand, sun = year()
        shares, before = [], []
        for cap in (0.05, 0.20, 0.40, 0.60):
            y = pd.DataFrame({"demand": demand, "net": demand - cap * sun, "solar": cap * sun})
            t = mix_stress.tight_hours(y)
            shares.append(round(100.0 * float((t["solar"] / cap).mean()), 1))
            before.append(round(100.0 * float((y.nlargest(100, "net")["solar"] / cap).mean()), 1))
        print(f"solar in the tightest hours, percent of capacity, at capacity 5, 20, 40, 60 percent of the peak: before {before}, after {shares}")
        self.assertEqual(len(set(shares)), 1)          # the measure no longer moves with capacity alone
        self.assertGreater(shares[0], 50.0)
        self.assertTrue(all(a > b for a, b in zip(before, before[1:])))

    def test_the_words(self):
        with open(os.path.join(ROOT, "docs", "methods", "grid_stress.md"), encoding="utf-8") as f:
            self.assertIn("| The tightest hours | The 100 used hours of the year with the highest demand", f.read())


if __name__ == "__main__":
    unittest.main()
