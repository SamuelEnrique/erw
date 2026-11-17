"""Ruling alternative 5 of /contracts (session 7701, 17 November 2026, branch wip/alt-contracts-5; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-contracts-2026-11-17.md, line 5): should the
capacity list give, beside each price filed as a number, a second figure in USD per kW-month? On this branch it does
(site/lib/contracts.ts kwMonth; 1 $/KW-DAY = 30.4375 $/KW-MO). No figure that stands moves; figures are added.

Pinned, where the internal table is on the machine (warehouse/output, or the folder ERW_TABLES_DIR names), with the page's
own library (site/scripts/alt-contracts-figures.mjs, handed the rows in a temporary file, never written to the
repository): 2026 Q2 capacity, 100 rows drawn, 50 figures added, median USD 5.01 per kW-month (1.83 to 15.45); 2026 Q1,
203 rows drawn, 92 added (a row with no unit is not converted), median 6.97, the most 8,845 (a row filed in $/KW-MO
whose number reads as $/MW-MO). The made-up rows are in site/scripts/test-contracts-render.mjs.

    python -m unittest tests.test_alt_contracts_5 -v
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
        cls.q1 = figures(quarter_rows(d, "2026-01-01", "2026-04-01"))

    def test_2026_q2(self):
        f = self.q2
        self.assertEqual((f["drawn"], f["converted"]), (100, 50))
        self.assertEqual((round(f["median"], 2), round(f["least"], 3), round(f["most"], 2)), (5.01, 1.826, 15.45))

    def test_2026_q1(self):
        f = self.q1
        self.assertEqual((f["drawn"], f["converted"]), (203, 92))
        self.assertEqual((round(f["median"], 2), round(f["most"], 2)), (6.97, 8845.0))


if __name__ == "__main__":
    unittest.main()
