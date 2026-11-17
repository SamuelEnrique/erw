"""Session 7051 (chain 370, the data machine): done-line request 181.

site/data/curtailment/worth.json said "no whole month is held" for ERCOT while ercot.json held October 2026 whole (744
of 744 hours). A local month whose every hour is held is now a whole month, valued per hub by the same rule as CAISO's
months (warehouse/derived/curtailment_worth.py, value_of).
"""

import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def ercot(o):
    if isinstance(o, dict):
        if o.get("name") == "ERCOT":
            return o
        for v in o.values():
            r = ercot(v)
            if r:
                return r
    if isinstance(o, list):
        for v in o:
            r = ercot(v)
            if r:
                return r
    return None


class ERCOTsWholeMonths(unittest.TestCase):
    def test_the_whole_months_are_written_and_valued(self):
        with open(os.path.join(ROOT, "site", "data", "curtailment", "worth.json"), encoding="utf-8") as f:
            e = ercot(json.load(f))
        self.assertIn("2026-10", e["months"])
        self.assertEqual(e["months"]["2026-10"]["hours"], 744)
        self.assertTrue(e["months_missing"].startswith("whole months held: "))
        rt = e["hubs"]["HB_HUBAVG"]["rt"]
        m = rt["months"]["2026-10"]
        self.assertEqual((m["hours_in_month"], m["days_held"]), (744, 31))
        self.assertAlmostEqual(m["curtailed_mwh"], e["months"]["2026-10"]["below_hsl_mwh"], places=1)
        self.assertGreater(m["value_usd"], 0)


if __name__ == "__main__":
    unittest.main()
