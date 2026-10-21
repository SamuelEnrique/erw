"""Session 524: EIA-923 from 2001. The default years run from 2001 to 2024 and the ceiling holds them (about 6 pages a
year); the rows are session 510's, held by tests/test_session510.py.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import eia923_plant_fuel as E  # noqa: E402


class TheYears(unittest.TestCase):
    def test_from_2001(self):
        self.assertEqual((E.FIRST, E.LAST), (2001, 2024))
        self.assertGreaterEqual(E.CEILING, 5 * (E.LAST - E.FIRST + 1))

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia923_plant_fuel.py", "tests/test_session524.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()
