"""Ruling alternative 1 of /contracts (session 7701, 17 November 2026, branch wip/alt-contracts-1; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-contracts-2026-11-17.md, line 1): should
"MW filed" in the largest buyers and sellers leave out a row filed above the megawatts view's ceiling (the largest
station operating in the United States, 6,809.0 MW in EIA-860M of the load of 5 October 2026)? On this branch it does.

The rule is pinned on rows made up here (every name is made up). When the internal table is on the machine
(warehouse/output, or the folder ERW_TABLES_DIR names), the figure is pinned on it too, by place and percent only: no
party's name and no party's own figure is written (the table is internal). Under main's rule the energy buyers' places 18
and 22 carry rows above the ceiling; under this choice place 18 falls by 100.0 percent and place 22 by 99.9 percent, and
the energy column over every party falls from 15,438,102.6 to 382,365.6 MW.

    python -m unittest tests.test_alt_contracts_1 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import eqr_buyers as eb  # noqa: E402

TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")


def frame(rows):
    return pd.DataFrame([dict(x_company_id=c, x_contract_unique_id=k, x_customer_company_name=b, x_product_name=p, status="in_force", mw=mw,
                              x_seller_company_name=f"Seller {c}", x_quarter="2026_Q2") for c, k, b, p, mw in rows])


def totals_of(d, ceiling):
    counts = d["x_customer_company_name"].value_counts().to_dict()
    mapping, _ = eb.groups_of(counts)
    totals, _ = eb.party_totals(d, mapping, eb.display_names(mapping, counts), ceiling=ceiling)
    return {(r["role"], r["product"], r["rank"]): r for r in totals}


class TheRule(unittest.TestCase):
    rows = [("C1", "K1", "Example Power Company", "ENERGY", "50"), ("C1", "K2", "Example Power Company", "ENERGY", "9000"),
            ("C2", "K1", "Example Power Company", "ENERGY", "6809"), ("C2", "K3", "Sample Energy LLC", "ENERGY", "")]

    def test_main_rule_keeps_every_row(self):
        b = totals_of(frame(self.rows), None)[("buyer", "energy", 1)]
        self.assertEqual((b["mw_filed"], b["rows_with_mw"], b["rows_over_mw"]), (15859.0, 3, 0))

    def test_the_other_choice_leaves_out_a_row_above_the_ceiling(self):
        t = totals_of(frame(self.rows), 6809.0)
        b = t[("buyer", "energy", 1)]
        self.assertEqual((b["mw_filed"], b["rows_with_mw"], b["rows_over_mw"]), (6859.0, 2, 1))   # 6,809 itself is kept: the ceiling is a station's size
        s = {r["name"]: r for k, r in t.items() if k[0] == "seller"}
        self.assertEqual((s["Seller C1"]["mw_filed"], s["Seller C1"]["rows_over_mw"]), (50.0, 1))
        self.assertEqual((s["Seller C2"]["mw_filed"], s["Seller C2"]["rows_over_mw"]), (6809.0, 0))

    def test_the_builder_passes_the_megawatts_views_ceiling(self):
        with open(os.path.join(ROOT, "warehouse", "derived", "eqr_buyers.py"), encoding="utf-8") as f:
            code = f.read()
        self.assertIn("ceiling, _ = eqr_terms.largest_plant(inputs)", code)
        self.assertIn("party_totals(d, mapping, shown, ceiling=ceiling)", code)


@unittest.skipUnless(os.path.exists(os.path.join(TABLES, "ferc_eqr_contracts.csv")) and os.path.exists(os.path.join(TABLES, "eia860m_operating_generators.csv")),
                     "the internal table is not on this machine")
class OnTheInternalTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import eqr_terms
        cls.ceiling, _ = eqr_terms.largest_plant(TABLES)
        d, _ = eb.read_input(TABLES)
        counts = d["x_customer_company_name"].value_counts().to_dict()
        mapping, _ = eb.groups_of(counts)
        shown = eb.display_names(mapping, counts)
        cls.before = {(r["role"], r["product"], r["rank"]): r for r in eb.party_totals(d, mapping, shown)[0]}
        cls.after = {(r["role"], r["product"], r["rank"]): r for r in eb.party_totals(d, mapping, shown, ceiling=cls.ceiling)[0]}

    def test_the_ceiling(self):
        self.assertEqual(self.ceiling, 6809.0)

    def change(self, key):
        a, b = self.before[key]["mw_filed"], self.after[key]["mw_filed"]
        return round((b - a) / a * 100, 1)

    def test_energy_buyers_places_18_and_22(self):
        moved = [k[2] for k in self.before if k[:2] == ("buyer", "energy") and k[2] <= 25 and self.after[k]["rows_over_mw"] > 0]
        self.assertEqual(moved, [18, 22])
        self.assertEqual(self.change(("buyer", "energy", 18)), -100.0)
        self.assertEqual(self.change(("buyer", "energy", 22)), -99.9)
        self.assertEqual((self.after[("buyer", "energy", 18)]["rows_over_mw"], self.after[("buyer", "energy", 22)]["rows_over_mw"]), (1, 25))

    def test_no_other_list_of_the_first_25_moves(self):
        for role in ("buyer", "seller"):
            for product in ("energy", "capacity", "tolling"):
                if (role, product) == ("buyer", "energy"):
                    continue
                moved = [k for k in self.before if k[:2] == (role, product) and k[2] <= 25 and self.after[k]["mw_filed"] != self.before[k]["mw_filed"]]
                self.assertEqual(moved, [], f"{role} {product}")

    def test_the_column_over_every_party(self):
        for product, a, b in (("energy", 15438102.6, 382365.6), ("capacity", 168997.3, 86280.2)):
            before = round(sum(r["mw_filed"] for k, r in self.before.items() if k[:2] == ("buyer", product)), 1)
            after = round(sum(r["mw_filed"] for k, r in self.after.items() if k[:2] == ("buyer", product)), 1)
            self.assertAlmostEqual(before, a, delta=1.0)
            self.assertAlmostEqual(after, b, delta=1.0)


if __name__ == "__main__":
    unittest.main()
