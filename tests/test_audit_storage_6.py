"""Session 10212 (storage audit, finding 6): two of /storage's fleet cells hold less, or more, than their names say.

The fleet tab's note read "Nameplate MW of every battery unit (prime mover BA) in EIA-860M, by EIA's status". Measured on
EIA-860M's September 2026 inventory (docs/reviews/storage-model-audit-2026-11-26/measures.json):
- "Operating" is the operating sheet, EIA's statuses OP, SB, OS and OA (warehouse/derived/storage_buildout.py says so
  for the build-out). 22 of its 1,156 units, 508.0 of 56,120.7 MW, are on standby (SB, 2 MW), out of service and not
  expected back next year (OS, 144 MW) or out of service and expected back (OA, 362 MW).
- "Retired" is eia860m_retired_generators, which keeps the inventory's year and the year before: 8 units, 338.5 MW,
  retired 2025-01 to 2026-02. EIA's full list (eia860m_retired_generators_all, August 2026) holds 50 retired battery
  units, 524.3 MW.

Words only (site/app/storage/page.tsx, FLEET_STATUS_WORDS in the fleet's note): no figure moves.
"""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class FleetCells(unittest.TestCase):
    def test_what_the_tables_hold(self):
        self.assertIn("Operating is EIA's operating inventory: statuses OP, SB, OS", read("warehouse", "derived", "storage_buildout.py"))
        self.assertIn('"retired": "eia860m_retired_generators"}', read("warehouse", "derived", "storage_capacity.py"))

    def test_the_note_says_so(self):
        p = read("site", "app", "storage", "page.tsx")
        self.assertIn('const FLEET_STATUS_WORDS = "Operating is EIA\'s operating inventory, which also counts units on standby and units out of service (EIA\'s codes SB, OS and OA). Retired holds only the units retired in the inventory\'s year and the year before', p)
        self.assertIn("MWh is never estimated from MW. ${FLEET_STATUS_WORDS}`}>", p)
        self.assertNotIn(chr(0x2014), p)


if __name__ == "__main__":
    unittest.main()
