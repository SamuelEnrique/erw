"""Session 10210 (curtailment audit, finding 1): a held grid's price figure reaches /curtailment.

On /curtailment?grid=isone and ?grid=nyiso the page swaps "Where free energy is" and "What it is worth" for the
licence words (licenseHeldGrid in site/app/curtailment/page.tsx), yet the summary sentence ("Its place with the most
hours under USD 5 ... is INTERNAL, with 1") and the third headline ("Most hours under USD 5") print a count from
free_energy.json, which those places read from iso_hub_prices_history, a table marked "license needed" for ISO-NE and
NYISO from 21 October 2026. Drawn on 26 November 2026: ISO-NE 1 hour (INTERNAL, October 2026), NYISO 17 hours (N.Y.C.,
the twelve months to October 2026).

These tests show the fault on main (they pass there). The fix would remove a figure a reader sees, so it is not made:
for Samuel's ruling, default "left as it is" (the page is in review; no visitor sees it).
"""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class HeldGridFigure(unittest.TestCase):
    def test_the_price_table_is_license_needed_for_isone_and_nyiso(self):
        st = json.loads(read("site", "data", "license_status.json"))
        row = st.get("iso_hub_prices_history") or st.get("tables", {}).get("iso_hub_prices_history")
        self.assertIsNotNone(row)
        self.assertEqual(row["status"], "license needed")
        self.assertIn("ISO-NE", row["publishers"])
        self.assertIn("NYISO", row["publishers"])

    def test_the_page_file_holds_counts_for_the_held_grids_from_that_table(self):
        f = json.loads(read("site", "data", "curtailment", "free_energy.json"))
        for grid, place in (("isone", ".H.INTERNAL_HUB"), ("nyiso", "N.Y.C.")):
            loc = next(l for l in f["grids"][grid]["locations"] if l["id"] == place)
            self.assertTrue(any("under5" in loc[w] for w in ("month", "year")), f"{grid} {place} holds a count")
            tables = {t for ts in loc["tables"].values() for t in ts}
            self.assertTrue(tables & {"iso_hub_prices_history", "iso_zone_prices_history"}, tables)

    def test_the_summary_and_headline_print_the_count_without_the_licence_gate(self):
        p = read("site", "app", "curtailment", "page.tsx")
        # the count is computed for every grid with a price file, before and outside the licence gate
        cheap = re.search(r"const cheap = top \?(.*?)\n", p).group(1)
        self.assertIn("top.win.under5", cheap)
        self.assertNotIn("licenseHeldGrid", cheap)
        top = re.search(r"const top = (.*?);\n", p).group(1)
        self.assertNotIn("licenseHeldGrid", top)
        # the branch for a grid with no curtailment figure (ISO-NE, NYISO) prints both
        self.assertIn('<>{g.name}: no curtailment figure is in the ERW. {cheap}</>', p)
        tail = p[p.index('<HeadlineNumber label={`Curtailed, ${g.name}`}'):]
        self.assertIn("label={`Most hours under USD ${free.threshold_usd_per_mwh}`} value={top ? <N k=\"head|cheap\">{whole(top.win.under5)}</N>", tail[:1500])


if __name__ == "__main__":
    unittest.main()
