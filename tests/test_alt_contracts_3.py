"""Ruling alternative 3 of /contracts (session 7701, 17 November 2026, branch wip/alt-contracts-3; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-contracts-2026-11-17.md, line 3): should a row
whose buyer is a market operator (PJM, MISO, SPP, ERCOT, CAISO, ISO New England, NYISO, by the words of the name filed) be
left out of "rows signed"? On this branch it is, in the page's library (site/lib/contracts.ts, withoutOperators).

The figure is pinned with the site's own code: the rows of the internal table for a quarter are handed to
site/scripts/alt-contracts-figures.mjs in a temporary file (never written to the repository). Runs only where the table
is on the machine (warehouse/output, or the folder ERW_TABLES_DIR names). Under main's rule 2026 Q2 lists 227 rows of
energy, capacity and tolling; under this choice 192 (-15.4 percent); energy 126 to 100, capacity 100 to 91; 2025 Q4 311 to
263. The made-up rows of the rule are in site/scripts/test-contracts-render.mjs.

    python -m unittest tests.test_alt_contracts_3 -v
"""

import json
import os
import subprocess
import tempfile
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
CSV = os.path.join(TABLES, "ferc_eqr_contracts.csv")
COLS = {"x_seller_company_name": "seller", "x_customer_company_name": "buyer", "x_contract_affiliate": "affiliate", "x_contract_service_agreement_id": "agreement",
        "x_product_type_name": "product_type", "x_product_name": "product", "x_class_name": "class", "x_term_name": "term",
        "x_commencement_date_of_contract_term": "commencement", "x_contract_termination_date": "termination", "x_quantity": "quantity", "x_units": "units",
        "x_rate": "rate", "x_rate_units": "rate_units", "x_rate_description": "rate_description", "x_point_of_delivery_balancing_authority": "pod_ba",
        "x_point_of_delivery_specific_location": "pod_location", "x_quarter": "quarter"}


def quarter_rows(d, first, end):
    """The rows the page reads for a quarter, as migration 020's function hands them (its columns, its order)."""
    q = d[(d["day"] >= first) & (d["day"] < end)].copy()
    q = q.rename(columns=COLS)
    q["event_date"] = q["day"]
    for c in ("mw", "price"):
        q[c] = None
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
        d = pd.read_csv(CSV, skiprows=n, dtype=str, keep_default_na=False, low_memory=False)
        d["day"] = d["event_date"].str.slice(0, 10)
        cls.q2 = figures(quarter_rows(d, "2026-04-01", "2026-07-01"))
        cls.q4 = figures(quarter_rows(d, "2025-10-01", "2026-01-01"))

    def test_2026_q2(self):
        self.assertEqual((self.q2["power"]["rows"], self.q2["power"]["left_out"]), (192, 35))
        self.assertEqual((self.q2["energy"]["rows"], self.q2["capacity"]["rows"], self.q2["tolling"]["rows"]), (100, 91, 1))

    def test_2025_q4(self):
        self.assertEqual((self.q4["power"]["rows"], self.q4["power"]["left_out"]), (263, 48))
        self.assertEqual((self.q4["energy"]["rows"], self.q4["capacity"]["rows"]), (174, 88))


if __name__ == "__main__":
    unittest.main()
