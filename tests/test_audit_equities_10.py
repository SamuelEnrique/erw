"""Audit of /equities, finding 10 (session 11403, docs/reviews/equities-model-audit-2026-11-28.md): the "Industry"
column reads "Silver Ores" for four coal miners.

American Resources (AREC), Core Natural Resources (CNR), Warrior Met Coal (HCC) and Ramaco Resources (METC) file
under SIC 1220, which the ERW's written rule reads as coal mining (warehouse/connectors/sec_edgar.py SIC_SEGMENTS,
the Coal segment); the list's `sic_label`, the SEC submissions file's own description as the connector keeps it, is
"Silver Ores", and the page prints it as each company's industry (site/app/equities/view.tsx, the table of every
company). The segment is right; the word beside it is not what the companies do.

The test shows it on main's files (it passes on main). The label is the data machine's file (the builder copies the
SEC's description): a data request to read the SEC's own list of SIC codes for 1220 and, if its name there is coal
mining, to write that name. Nothing is changed here."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
IDX = os.path.join(ROOT, "site", "data", "equities", "index.json")


class CoalLabel(unittest.TestCase):
    def test_four_coal_miners_called_silver(self):
        with open(IDX, encoding="utf-8") as f:
            cos = json.load(f)["companies"]
        c1220 = {c["ticker"]: c for c in cos if c["sic"] == "1220"}
        self.assertEqual(sorted(c1220), ["AREC", "CNR", "HCC", "METC"])
        for c in c1220.values():
            self.assertEqual(c["sic_label"], "Silver Ores")
            self.assertEqual(c["segments"], ["coal"])
        self.assertIn("COAL", c1220["HCC"]["name"].upper())


if __name__ == "__main__":
    unittest.main()
