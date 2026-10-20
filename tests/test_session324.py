"""Session 324: the licenses.

Energy Research Warehouse (ERW). No network.

  1. A disagreement a newer record settles is ruled, not open: the "license needed" rows of license_status.csv, and
     PortWatch kept internal with the IMF's reason.
  2. CARB's auction prices and the RRC's lease production are flagged public: the document's clause wins.
  3. The lists for Samuel: the 42 permission tables by publisher with a tick box each, and the 19 unsettled.

    python -m unittest tests.test_session324 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import licenses as L  # noqa: E402


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Ruled(unittest.TestCase):
    def test_portwatch_stays_internal_with_its_reason(self):
        why = L.RULED_INTERNAL["portwatch_chokepoint_transits"]
        self.assertIn("prohibit bulk download", why)
        self.assertIn("copyright@imf.org", why)

    def test_license_needed_rows_are_read(self):
        needed = L.license_needed()
        self.assertIn("grid_stress_days", needed)
        self.assertTrue(all(v for v in needed.values()))

    def test_the_document_says_so(self):
        doc = src("docs", "licenses.md")
        self.assertIn("## Settled by a ruling (session 324)", doc)
        self.assertIn("`portwatch_chokepoint_transits`: kept internal by the owner's default of 19 October 2026", doc)


class Flags(unittest.TestCase):
    def test_carb_and_rrc_are_public(self):
        self.assertIn('"License: public (session 324', src("warehouse", "connectors", "carbon_auctions.py"))
        self.assertIn('"License: public (session 324', src("warehouse", "connectors", "rrc_production.py"))
        self.assertNotIn("CARB terms for this summary are unconfirmed", src("warehouse", "connectors", "carbon_auctions.py"))


class Lists(unittest.TestCase):
    def test_the_permission_list(self):
        doc = src("docs", "state", "permissions_2026-10-19.md")
        self.assertIn("The 42 are session 205's", doc)
        self.assertGreaterEqual(doc.count("- [ ] `"), 42)
        self.assertIn("## Joined since session 205", doc)

    def test_the_unsettled_list(self):
        doc = src("docs", "state", "unsettled_licenses_2026-10-19.md")
        self.assertIn("Nothing was sent to anyone.", doc)
        for t in ("eia_all_futures_prices", "texas_transmission_matrix", "news_scores_shadow", "large_load_public"):
            self.assertIn(f"`{t}`", doc)


if __name__ == "__main__":
    unittest.main()
