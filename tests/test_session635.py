"""Session 635: the early window of the refinery input and production connectors. Months before SPLIT are a window of
their own ending at EARLY_END, so the 2015 on pages of sessions 615 and 618 (asked without an end) answer again.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import eia_refinery_inputs as I  # noqa: E402
import eia_refinery_production as P  # noqa: E402


class TheWindows(unittest.TestCase):
    def test_the_split(self):
        for m in (I, P):
            self.assertEqual((m.SPLIT, m.EARLY_END, m.FIRST), ("2015-01", "2014-12", "2015-01"))

    def test_the_ceilings_fit_a_session(self):
        for m in (I, P):
            self.assertLessEqual(m.CEILING, 37)

    def test_no_em_dash(self):
        for f in ("eia_refinery_inputs.py", "eia_refinery_production.py"):
            with open(os.path.join(ROOT, "warehouse", "connectors", f), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()
