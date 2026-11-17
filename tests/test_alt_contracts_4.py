"""Ruling alternative 4 of /contracts (session 7701, 17 November 2026, branch wip/alt-contracts-4; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-contracts-2026-11-17.md, line 4): should the first
view count its list by contract (filer and contract identifier) and merged buyer name, as the other three views do? On
this branch it does: the loader puts x_buyer_counted_as on each contract row (load.buyer_counted_as, from
ferc_eqr_buyer_names), migration 038 answers filer, contract_id and buyer_merged, and site/lib/contracts.ts contractCounts
counts by them.

Pinned, where the internal table is on the machine (warehouse/output, or the folder ERW_TABLES_DIR names), with the
loader's own function and the page's own library (site/scripts/alt-contracts-figures.mjs, handed the rows in a temporary
file, never written to the repository): 2026 Q2, energy, capacity and tolling, 174 agreements to 175 contracts, 78
sellers to 78, 95 buyers to 86; 2026 Q1 buyers 161 to 136; 2025 Q4 213 to 214 contracts, buyers 143 to 135.

    python -m unittest tests.test_alt_contracts_4 -v
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
sys.path.insert(0, os.path.join(ROOT, "warehouse", "supabase"))
TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
CSV = os.path.join(TABLES, "ferc_eqr_contracts.csv")
COLS = {"x_seller_company_name": "seller", "x_customer_company_name": "buyer", "x_contract_affiliate": "affiliate", "x_contract_service_agreement_id": "agreement",
        "x_product_type_name": "product_type", "x_product_name": "product", "x_class_name": "class", "x_term_name": "term",
        "x_commencement_date_of_contract_term": "commencement", "x_contract_termination_date": "termination", "x_quantity": "quantity", "x_units": "units",
        "x_rate": "rate", "x_rate_units": "rate_units", "x_rate_description": "rate_description", "x_point_of_delivery_balancing_authority": "pod_ba",
        "x_point_of_delivery_specific_location": "pod_location", "x_quarter": "quarter",
        "x_company_id": "filer", "x_contract_unique_id": "contract_id", "x_buyer_counted_as": "buyer_merged"}   # migration 038's three


def quarter_rows(d, first, end):
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


class TheLoader(unittest.TestCase):
    def test_a_contract_row_carries_its_buyers_merged_name(self):
        import load
        with tempfile.TemporaryDirectory() as tmp:
            pd.DataFrame([dict(entity_id="n1", name="EXAMPLE POWER CO.", x_counted_as="Example Power Company"),
                          dict(entity_id="n2", name="Example Power Company", x_counted_as="Example Power Company")]).to_csv(os.path.join(tmp, "ferc_eqr_buyer_names.csv"), index=False)
            keep, load.OUT = load.OUT, tmp
            try:
                got = load.buyer_counted_as(pd.DataFrame({"event_id": ["a", "b", "c"], "x_customer_company_name": ["EXAMPLE POWER CO.", "Example Power Company", "Sample Energy LLC"]}))
            finally:
                load.OUT = keep
        self.assertEqual(list(got["x_buyer_counted_as"]), ["Example Power Company", "Example Power Company", "Sample Energy LLC"])

    def test_no_names_table_leaves_the_rows_as_they_are(self):
        import load
        with tempfile.TemporaryDirectory() as tmp:
            keep, load.OUT = load.OUT, tmp
            try:
                got = load.buyer_counted_as(pd.DataFrame({"event_id": ["a"], "x_customer_company_name": ["Sample"]}))
            finally:
                load.OUT = keep
        self.assertNotIn("x_buyer_counted_as", got.columns)

    def test_the_names_table_stays_out_of_the_live_set(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertNotIn("ferc_eqr_buyer_names", f.read().split("catalogue_hold")[0].replace("# ", "#"))


@unittest.skipUnless(os.path.exists(CSV) and os.path.exists(os.path.join(TABLES, "ferc_eqr_buyer_names.csv")), "the internal tables are not on this machine")
class OnTheInternalTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import load
        keep, load.OUT = load.OUT, TABLES
        try:
            d = load.buyer_counted_as(load.read_table("ferc_eqr_contracts"))
        finally:
            load.OUT = keep
        d["day"] = d["event_date"].str.slice(0, 10)
        cls.f = {q: figures(quarter_rows(d, a, b)) for q, a, b in (("2026-Q2", "2026-04-01", "2026-07-01"), ("2026-Q1", "2026-01-01", "2026-04-01"), ("2025-Q4", "2025-10-01", "2026-01-01"))}

    def got(self, q):
        p = self.f[q]["power"]
        return (p["agreements_as_main"], p["contracts"]), (p["sellers_as_main"], p["sellers"]), (p["buyers_as_main"], p["buyers"]), p["by_contract"]

    def test_2026_q2(self):
        self.assertEqual(self.got("2026-Q2"), ((174, 175), (78, 78), (95, 86), True))

    def test_2026_q1(self):
        self.assertEqual(self.got("2026-Q1"), ((243, 243), (102, 102), (161, 136), True))

    def test_2025_q4(self):
        self.assertEqual(self.got("2025-Q4"), ((213, 214), (134, 134), (143, 135), True))


if __name__ == "__main__":
    unittest.main()
