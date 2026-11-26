"""Session 10000 (chain 701, data request 57 of docs/state/data_requests_five_tools.md): ba_supply.py's trial (--out-dir)
keeps reading the EIA-930 extracts from warehouse/raw. iso_prices.set_out_dir moves the raw folder too, so the trial had
built every balance from nothing and written no share, without a word. No build is run here."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class TheTrialKeepsTheRawFolder(unittest.TestCase):
    def test_the_raw_folder_is_put_back(self):
        with open(os.path.join(ROOT, "warehouse", "derived", "ba_supply.py"), encoding="utf-8") as f:
            s = f.read()
        i = s.index("ip.set_out_dir(a.out_dir)")
        self.assertIn("raw_dir = ip.RAW_DIR", s[i - 200:i])
        self.assertIn("ip.RAW_DIR = raw_dir", s[i:i + 80])

    def test_the_extracts_are_read_from_ip_raw_dir(self):
        with open(os.path.join(ROOT, "warehouse", "connectors", "eia930_emissions.py"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn('os.path.join(ip.RAW_DIR, "eia930_emissions"', s)


if __name__ == "__main__":
    unittest.main()
