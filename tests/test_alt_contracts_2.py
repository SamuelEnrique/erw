"""Ruling alternative 2 of /contracts (session 7701, 17 November 2026, branch wip/alt-contracts-2; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-contracts-2026-11-17.md, line 2): is a rate filed
as the number 0 a price, in "Rows with a price as a number"? On this branch it is not: the first view counts the priced
rows with site/lib/contracts.ts pricedNotZero, and the builder warehouse/derived/eqr_terms.py gives a rate filed as 0 its
own kind, "zero", so that the terms view's "rows that file their rate as a number" leaves it out.

Pinned on rows made up here, and, where the internal table is on the machine (warehouse/output, or the folder
ERW_TABLES_DIR names), on it, with the page's own library (site/scripts/alt-contracts-figures.mjs, handed the rows in a
temporary file) and the builder's own function: 2026 Q2, energy, capacity and tolling, 112 to 95 of 227 rows; energy 56
to 45; capacity 56 to 50; 2025 Q4 104 to 65; the terms view over the quarter's file 81,718 to 44,643 (37,075 zeros).

    python -m unittest tests.test_alt_contracts_2 -v
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import eqr_terms as et  # noqa: E402

TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
CSV = os.path.join(TABLES, "ferc_eqr_contracts.csv")
COLS = {"x_seller_company_name": "seller", "x_customer_company_name": "buyer", "x_contract_affiliate": "affiliate", "x_contract_service_agreement_id": "agreement",
        "x_product_type_name": "product_type", "x_product_name": "product", "x_class_name": "class", "x_term_name": "term",
        "x_commencement_date_of_contract_term": "commencement", "x_contract_termination_date": "termination", "x_quantity": "quantity", "x_units": "units",
        "x_rate": "rate", "x_rate_units": "rate_units", "x_rate_description": "rate_description", "x_point_of_delivery_balancing_authority": "pod_ba",
        "x_point_of_delivery_specific_location": "pod_location", "x_quarter": "quarter"}


def quarter_rows(d, first, end):
    """The rows the page reads for a quarter, as migration 020's function hands them (its columns, its order)."""
    q = d[(d["day"] >= first) & (d["day"] < end)].copy().rename(columns=COLS)
    q["event_date"] = q["day"]
    q["mw"], q["price"] = None, None
    q = q.sort_values(["event_date", "seller", "event_id"], ascending=[False, True, True])
    keep = ["event_id", "event_date", "status", "mw", "price"] + list(COLS.values())
    return [{k: (None if (v is None or v == "") and k not in ("rate", "rate_description") else v) for k, v in r.items()} for r in q[keep].to_dict("records")]


def figures(rows):
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "rows.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(rows, f)
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-contracts-figures.mjs", path], cwd=SITE, capture_output=True, text=True, timeout=300)
    if p.returncode != 0:
        raise AssertionError(p.stderr[-2000:])
    return json.loads(p.stdout)


def kinds(d):
    """The builder's own x_rate_kind for the rows of d (et.terms, every other input left empty)."""
    seen = pd.DataFrame({"k": et.contract_key(d), "q": d["x_quarter"]}).drop_duplicates()
    t = et.terms(d, {}, seen.groupby("k")["q"].min(), seen.groupby("k")["q"].nunique(), "2026-11-17T00:00:00Z", 6809.0)
    return t["x_rate_kind"].value_counts().to_dict()


class TheRule(unittest.TestCase):
    def test_the_builder_reads_a_zero_as_its_own_kind(self):
        rows = [("1", "$/MWH", ""), ("0", "$/MWH", ""), ("0.00", "$/KW-MO", ""), ("", "", "Market Based"), ("", "", "")]
        d = pd.DataFrame([dict(event_id=f"e{i}", event_date="2026-06-01", x_rate=r, x_rate_units=u, x_rate_description=w, x_quantity="", x_units="",
                               x_customer_company_name="Example Buyer", x_seller_company_name="Example Seller", x_company_id="C1", x_contract_unique_id=f"K{i}",
                               x_product_name="ENERGY", x_quarter="2026_Q2", status="in_force") for i, (r, u, w) in enumerate(rows)])
        for c in list(et.TERM_COLS) + list(et.PRODUCT_FIELDS) + list(getattr(et, "STORAGE_COLS", [])):
            if c not in d.columns:
                d[c] = ""
        self.assertEqual(kinds(d), {"zero": 2, "number": 1, "words": 1, "none": 1})


@unittest.skipUnless(os.path.exists(CSV), "the internal table is not on this machine")
class OnTheInternalTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        n = 0
        with open(CSV, encoding="utf-8") as f:
            for line in f:
                if not line.startswith("#"):
                    break
                n += 1
        cls.d = pd.read_csv(CSV, skiprows=n, dtype=str, keep_default_na=False, low_memory=False)
        cls.d["day"] = cls.d["event_date"].str.slice(0, 10)

    def test_the_first_view(self):
        q2 = figures(quarter_rows(self.d, "2026-04-01", "2026-07-01"))
        self.assertEqual((q2["power"]["rows"], q2["power"]["priced_as_main"], q2["power"]["priced"]), (227, 112, 95))
        self.assertEqual((q2["energy"]["priced"], q2["capacity"]["priced"]), (45, 50))
        q4 = figures(quarter_rows(self.d, "2025-10-01", "2026-01-01"))
        self.assertEqual((q4["power"]["rows"], q4["power"]["priced_as_main"], q4["power"]["priced"]), (311, 104, 65))

    def test_the_terms_view(self):
        k = kinds(self.d.drop(columns=["day"]))
        self.assertEqual((k.get("number"), k.get("zero")), (44643, 37075))


if __name__ == "__main__":
    unittest.main()
