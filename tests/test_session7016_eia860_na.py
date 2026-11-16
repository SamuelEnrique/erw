"""Session 7016 (chain 301, done-line request 33): EIA-860M's text NA is read as printed. Two generators whose id EIA
prints as NA (plants 62844 and 64835, vintage 2026-09) were held with no generator id, because pandas' default missing
values turned the text into nothing. A balancing authority code of NA is still written blank (not stated). No request,
no model call."""
import io
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import eia860  # noqa: E402


def workbook(rows):
    buf = io.BytesIO()
    head = pd.DataFrame([["Inventory of Operating Generators as of September 2026"], [""]])
    cols = ["Plant ID", "Generator ID", "Balancing Authority Code"]
    with pd.ExcelWriter(buf) as w:
        head.to_excel(w, sheet_name="Operating", header=False, index=False)
        pd.DataFrame(rows, columns=cols).to_excel(w, sheet_name="Operating", startrow=2, index=False)
    return buf.getvalue()


class TheText(unittest.TestCase):
    def test_na_is_an_id_and_a_blank_is_a_blank(self):
        d, title = eia860.read_sheet(workbook([["62844", "NA", "CISO"], ["64835", "NA", "NA"], ["1", "GEN1", None]]), "Operating")
        self.assertIn("September 2026", title)
        self.assertEqual(list(d["Generator ID"]), ["NA", "NA", "GEN1"])
        self.assertEqual(list(d["Balancing Authority Code"].fillna("")), ["CISO", "NA", ""])

    def test_the_balancing_authority_na_is_written_blank(self):
        with open(os.path.join(ROOT, "warehouse", "connectors", "eia860.py"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn('d["Balancing Authority Code"].mask(d["Balancing Authority Code"] == "NA", "")', s)
        self.assertIn("keep_default_na=False", s)


if __name__ == "__main__":
    unittest.main()
