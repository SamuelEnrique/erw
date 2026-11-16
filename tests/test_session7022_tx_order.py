"""Session 7022 (chain 301, the data machine, 16 November 2026): done-line request 45.

The Commission's Order in Docket No. 59080 (item 88, filed 5 November 2026) approves both 2026 transmission-charge
matrices of Commission Staff's filing of 16 March 2026: matrix A for billing from 1 January to 11 March 2026, matrix B
from 12 March 2026. Until this session the connector called both "filed" with "not approved" beside them, read from
the filing list of 7 October 2026 (86 items, the proceeding remanded on 4 June 2026). This test holds the connector to
the Order: both 2026 matrices approved, the Order's words beside each, and the Order among the documents it names.
"""

import importlib.util
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def connector():
    path = os.path.join(ROOT, "warehouse", "connectors", "texas_transmission_matrix.py")
    spec = importlib.util.spec_from_file_location("texas_transmission_matrix_7022", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TheOrderOfFiveNovember(unittest.TestCase):
    def setUp(self):
        self.m = connector()

    def test_both_2026_matrices_are_approved_with_the_orders_words(self):
        a, b = self.m.READS["attach_2026_a"], self.m.READS["attach_2026_b"]
        self.assertEqual((a["status"], b["status"]), ("approved", "approved"))
        for r, matrix, start in ((a, "matrix A", "January 1, 2026 through March 11, 2026"), (b, "matrix B", "beginning on March 12, 2026")):
            self.assertIn("Order filed 2026-11-05 (Docket No. 59080, item 88)", r["docket_status"])
            self.assertIn("The Commission approves the 2026 final transmission-charge " + matrix, r["docket_status"])
            self.assertIn(start, r["docket_status"])
            self.assertNotIn("not approved", r["docket_status"])

    def test_2025_stands_as_it_was(self):
        self.assertEqual(self.m.READS["attach_2025"]["status"], "approved")
        self.assertIn("Order filed 2025-06-05", self.m.READS["attach_2025"]["docket_status"])

    def test_the_order_is_a_named_document_within_the_allowance(self):
        d = self.m.DOCS["order_2026"]
        self.assertEqual(d["address"], "https://interchange.puc.texas.gov/Documents/59080_88_1699841.PDF")
        self.assertEqual((d["docket"], d["item"], d["date_filed"], d["kind"]), ("59080", "88", "11/5/2026", "order"))
        self.assertIn("item_59080_88", self.m.DOCS)
        self.assertEqual(self.m.MAX_DOCUMENTS, 20)


if __name__ == "__main__":
    unittest.main()
