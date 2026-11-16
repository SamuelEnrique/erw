"""Session 7019 (chain 301, done-line request 21): EIA's balancing authorities, code and name, as a site file for the
contracts page, from EIA's EIA-930 reference tables (public domain). Nothing of the internal EQR tables is in it. No
request, no model call."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class TheFile(unittest.TestCase):
    def test_the_authorities_and_their_source(self):
        with open(os.path.join(ROOT, "site", "data", "eia930_ba_names.json"), encoding="utf-8") as f:
            d = json.load(f)
        a = d["authorities"]
        self.assertGreaterEqual(len(a), 50)
        self.assertEqual(d["count"], len(a))
        for code in ("CPLE", "DUK", "SOCO", "WACM", "BPAT", "ERCO", "CISO", "PJM"):
            self.assertIn(code, a)
            self.assertGreater(len(a[code]["name"]), 3)
        self.assertEqual(d["source_url"], "https://www.eia.gov/electricity/930-content/EIA930_Reference_Tables.xlsx")
        self.assertRegex(d["sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(set(next(iter(a.values()))), {"name", "time_zone", "region", "region_code", "us"})


if __name__ == "__main__":
    unittest.main()
