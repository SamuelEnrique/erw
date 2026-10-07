"""Session 140: the Commission's transmission charge matrix (warehouse/connectors/texas_transmission_matrix.py).

The sentence rule on a real page of the matrix, the column rule, the spend check that refuses a model call before it
is sent, and the providers' sum against the printed total.

The fixtures are real: tests/fixtures/session140/matrix/pages/attach_2025/p0001.txt, p0002.txt and p0018.txt are
pages 1, 2 and 18 of "Attach A-F.pdf", the attachments to Commission Staff's Final Transmission Charge Matrix (Public
Utility Commission of Texas, Docket No. 57491, item 51, filed 20 March 2025), as pdfplumber extracted them on
2026-10-07 from the item's ZIP, https://interchange.puc.texas.gov/Documents/57491_51_1481445.ZIP. The two files in
answers/ are the model's answers for pages 1 and 2 as they came (session 140, step texas_matrix_read).
"""

import importlib.util
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (os.path.join(ROOT, "warehouse", "connectors"), os.path.join(ROOT, "warehouse")):
    if p not in sys.path:
        sys.path.insert(0, p)

spec = importlib.util.spec_from_file_location(
    "texas_transmission_matrix", os.path.join(ROOT, "warehouse", "connectors", "texas_transmission_matrix.py"))
ttm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ttm)

FIX = os.path.join(ROOT, "tests", "fixtures", "session140", "matrix")


def page(n):
    with open(os.path.join(FIX, "pages", "attach_2025", f"p{n:04d}.txt"), encoding="utf-8") as f:
        return f.read()


ONCOR = "Oncor Electric Delivery ONC $1,488,366,495 55282 $19.401534 28,908,860.870"
TOTAL = "TOTAL $ 5 ,446,864,795 $68.547301 81,042,657"
STAMP = "Total ERCOT Postage Stamp Rate $/KW $68.547301"


class SentenceRule(unittest.TestCase):
    def test_the_rule_is_session_138s_own(self):
        self.assertIs(ttm.tdc.verify.__module__, ttm.tdc.norm.__module__)
        self.assertEqual(ttm.tdc.verify.__module__, "texas_delivery_charges")
        self.assertIs(ttm.MODEL, ttm.tdc.MODEL)

    def test_a_line_of_the_page_with_its_figure_is_kept(self):
        p2 = page(2)
        self.assertEqual(ttm.verify({"line": ONCOR, "value": "$19.401534"}, p2), (True, "", "$19.401534", False))
        self.assertEqual(ttm.verify({"line": ONCOR, "value": "$1,488,366,495"}, p2)[:2], (True, ""))
        self.assertEqual(ttm.verify({"line": ONCOR, "value": "28,908,860.870"}, p2)[:2], (True, ""))
        self.assertEqual(ttm.verify({"line": STAMP, "value": "$68.547301"}, p2)[:2], (True, ""))
        # whitespace normalized, nothing else
        self.assertTrue(ttm.verify({"line": "Oncor Electric  Delivery ONC $1,488,366,495 55282\n$19.401534 28,908,860.870",
                                    "value": "$19.401534"}, p2)[0])

    def test_a_line_altered_by_one_digit_is_rejected(self):
        p2 = page(2)
        bad = ONCOR.replace("$19.401534", "$19.401535")
        self.assertEqual(ttm.verify({"line": bad, "value": "$19.401535"}, p2)[:2], (False, "line not found on the page"))
        self.assertFalse(ttm.verify({"line": ONCOR, "value": "$19.401535"}, p2)[0])       # the value is not in its line
        self.assertFalse(ttm.verify({"line": ONCOR, "value": "9.401534"}, p2)[0])         # inside a longer number
        self.assertFalse(ttm.verify({"line": ONCOR, "value": "488,366"}, p2)[0])
        self.assertFalse(ttm.verify({"line": "", "value": "$19.401534"}, p2)[0])          # no number without its line
        self.assertFalse(ttm.verify({"line": ONCOR, "value": ""}, p2)[0])
        # a line of page 2 is not on page 1
        self.assertEqual(ttm.verify({"line": ONCOR, "value": "$19.401534"}, page(1))[:2], (False, "line not found on the page"))

    def test_a_value_that_is_not_one_number_is_rejected(self):
        p2 = page(2)
        self.assertEqual(ttm.verify({"line": ONCOR, "value": "$1,488,366,495 55282"}, p2)[:2], (False, "value is not one number"))
        self.assertEqual(ttm.verify({"line": ONCOR, "value": "about $19.401534"}, p2)[:2], (False, "value is not one number"))

    def test_digits_the_pages_text_sets_apart_are_kept_as_the_text_has_them_and_marked(self):
        p2 = page(2)
        self.assertIn(TOTAL, p2)       # the page's text really holds "$ 5 ,446,864,795"
        for given in ("$ 5 ,446,864,795", "$5,446,864,795"):
            ok, why, value, spaced = ttm.verify({"line": TOTAL, "value": given}, p2)
            self.assertEqual((ok, why, value, spaced), (True, "", "$ 5 ,446,864,795", True))
            self.assertEqual(ttm.tdc.decimal_of(ttm.squeezed(value)), "5446864795")
        # a piece of the spaced number is not the number, and one digit off is not on the page
        self.assertFalse(ttm.verify({"line": TOTAL, "value": "446,864,795"}, p2)[0])
        self.assertFalse(ttm.verify({"line": TOTAL, "value": "$5,446,864,796"}, p2)[0])
        # an unspaced figure of the same line is not marked
        self.assertEqual(ttm.verify({"line": TOTAL, "value": "81,042,657"}, p2), (True, "", "81,042,657", False))


class ColumnRule(unittest.TestCase):
    def test_the_figure_stands_at_its_columns_place(self):
        p2 = page(2)
        self.assertEqual(ttm.column_check("access_fee", "$19.401534", ONCOR, p2, True)[:2], (True, "Access Fee ($/KW) *"))
        self.assertEqual(ttm.column_check("transmission_cost_of_service", "$1,488,366,495", ONCOR, p2, True)[:2], (True, "TCOS"))
        self.assertEqual(ttm.column_check("average_4cp", "28,908,860.870", ONCOR, p2, True)[:2], (True, "Average 4CP (KW)"))
        self.assertTrue(ttm.column_check("average_4cp", "12,931.941", "Luling, City of LULG 12,931.941", p2, True)[0])
        self.assertTrue(ttm.column_check("total_transmission_cost_of_service", "$ 5 ,446,864,795", TOTAL, p2, True)[0])
        self.assertTrue(ttm.column_check("total_average_4cp", "81,042,657", TOTAL, p2, True)[0])
        self.assertTrue(ttm.column_check("postage_stamp_rate", "$68.547301", STAMP, p2, True)[0])

    def test_a_figure_named_for_another_column_is_not_checked(self):
        p2 = page(2)
        self.assertFalse(ttm.column_check("average_4cp", "$19.401534", ONCOR, p2, True)[0])
        self.assertFalse(ttm.column_check("access_fee", "28,908,860.870", ONCOR, p2, True)[0])
        self.assertFalse(ttm.column_check("transmission_cost_of_service", "55282", ONCOR, p2, True)[0])   # the docket number
        self.assertFalse(ttm.column_check("access_fee", "12,931.941", "Luling, City of LULG 12,931.941", p2, True)[0])

    def test_a_page_the_session_did_not_read_is_never_marked_checked(self):
        ok, header, how = ttm.column_check("access_fee", "$19.401534", ONCOR, page(2), False)
        self.assertEqual((ok, header), (False, "Access Fee ($/KW) *"))
        self.assertIn("not read by the session", how)

    def test_the_total_line_of_attachment_e_pairs_with_the_column_codes(self):
        p18 = page(18)
        codes, total, cut = ttm.e_lines(p18)
        self.assertEqual(codes[4], "TNMP")
        self.assertEqual(len(codes), len(total))
        self.assertEqual(codes[-1], "Total")
        line = "Total " + " ".join(total)
        self.assertIn(line, ttm.tdc.norm(p18))
        self.assertEqual(ttm.column_check("attachment_e_total_row", "$163,721,359", line, p18, True, "TNMP")[:2], (True, "TNMP"))
        self.assertFalse(ttm.column_check("attachment_e_total_row", "$163,721,359", line, p18, True, "TXLA")[0])
        self.assertFalse(ttm.column_check("attachment_e_total_row", "$163,721,359", line, p18, True, "NOPE")[0])
        # the cut page sent to the model keeps the heading, the codes and the Total line, and none of the rows between
        self.assertIn("What Column Entity Collects from Row Entity", cut)
        self.assertNotIn("\nAEP $", cut)


class SpendCheck(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.lines = []

    def patches(self, spent):
        import llm
        sent = []

        def no_client(*a, **k):
            sent.append(1)
            raise AssertionError("a model client was built although the call does not fit under the budget")
        return sent, [mock.patch.dict(os.environ, {"ERW_SESSION": "140", "ERW_SPEND_CAP_USD": "3.00"}),
                      mock.patch.object(llm, "session_total", lambda name=None: spent),
                      mock.patch.object(llm, "client", no_client),
                      mock.patch.object(ttm, "ANSWERS", os.path.join(self.tmp, "answers")),
                      mock.patch.object(ttm, "TEXTS", os.path.join(FIX, "pages"))]

    def test_the_worst_case_arithmetic_is_session_138s(self):
        price = {"input": 2.00, "output": 10.00}
        est = ttm.tdc.worst_case_usd(60000, 16000, price)     # 30,000 input tokens, 16,000 output tokens
        self.assertAlmostEqual(est, 0.22, places=9)
        self.assertTrue(ttm.tdc.fits(2.48, est, 2.70))
        self.assertFalse(ttm.tdc.fits(2.49, est, 2.70))

    def test_a_call_that_would_not_fit_is_refused_before_it_is_sent(self):
        sent, ps = self.patches(spent=2.60)        # USD 2.60 in the ledger; the page's worst case is about USD 0.17
        for p in ps:
            p.start()
            self.addCleanup(p.stop)
        self.assertEqual(ttm.read(["attach_2025_p1"], self.lines.append, "test", 2.70), 1)
        self.assertEqual(sent, [])
        self.assertTrue(any("REFUSED before the call" in x for x in self.lines), self.lines)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "answers", "attach_2025_p1__test.json")))

    def test_no_call_without_a_budget_or_without_a_session(self):
        sent, ps = self.patches(spent=0.0)
        for p in ps:
            p.start()
            self.addCleanup(p.stop)
        self.assertEqual(ttm.read(["attach_2025_p1"], self.lines.append, "test", None), 1)
        with mock.patch.dict(os.environ, {"ERW_SESSION": ""}):
            self.assertEqual(ttm.read(["attach_2025_p1"], self.lines.append, "test", 2.70), 1)
        self.assertEqual(sent, [])
        self.assertEqual(sum("REFUSED" in x for x in self.lines), 2)


class ProviderSum(unittest.TestCase):
    def gather(self):
        fake = {"doc_id": "native_2025", "retrieved_at": "2026-10-07T09:11:39Z"}
        with mock.patch.object(ttm, "TEXTS", os.path.join(FIX, "pages")), \
                mock.patch.object(ttm, "ANSWERS", os.path.join(FIX, "answers")), \
                mock.patch.object(ttm, "PLAN", [("attach_2025_p1", "attach_2025", [1]), ("attach_2025_p2", "attach_2025", [2])]), \
                mock.patch.object(ttm, "read_manifest", lambda: [fake]):
            lines = []
            kept, dropped, counts = ttm.gather(lines.append)
        return kept, dropped, counts, lines

    def test_every_figure_of_the_two_real_answers_is_on_its_page(self):
        kept, dropped, counts, lines = self.gather()
        self.assertEqual(dropped, [])
        c = counts["attach_2025"]
        self.assertEqual((c["returned"], c["kept"], c["dropped"], c["lines_missing"]), (176, 176, 0, 0))
        self.assertEqual(c["lines"], 101)           # 60 and 41 lines that end in a figure, all returned
        self.assertTrue(all(k["column_checked"] for k in kept))
        self.assertEqual([k["value_as_written"] for k in kept if k["spaced"]], ["$ 5 ,446,864,795"])

    def test_the_providers_costs_sum_to_the_printed_total(self):
        kept, _, _, _ = self.gather()
        figs = [{"doc_id": k["doc_id"], "quantity": k["quantity"], "amount": k["amount"]} for k in kept]
        s = ttm.sum_check(figs)["attach_2025"]
        self.assertEqual(s, {"providers": 47, "sum_of_providers": "5446864795", "printed_total": "5446864795",
                             "difference": "0", "agrees": True})
        # one provider left out, and the check says so
        short = [f for f in figs if not (f["quantity"] == "transmission_cost_of_service" and f["amount"] == "1488366495")]
        s = ttm.sum_check(short)["attach_2025"]
        self.assertEqual((s["providers"], s["agrees"], s["difference"]), (46, False, "-1488366495"))
        # no printed total kept: never said to agree
        none = [f for f in figs if f["quantity"] != "total_transmission_cost_of_service"]
        self.assertFalse(ttm.sum_check(none)["attach_2025"]["agrees"])

    def test_the_four_utilities_rows_as_printed(self):
        kept, _, _, _ = self.gather()
        got = {(tdc_code, k["quantity"]): k["value_as_written"] for k in kept
               for tdc_code in [ttm.tdc.norm(k["code"])] if tdc_code in ttm.UTILITY_OF}
        self.assertEqual(got[("ONC", "access_fee")], "$19.401534")
        self.assertEqual(got[("CNP", "access_fee")], "$7.927530")
        self.assertEqual(got[("AEP", "access_fee")], "$9.075870")
        self.assertEqual(got[("TNMP", "access_fee")], "$1.954246")
        self.assertEqual(got[("ONC", "transmission_cost_of_service")], "$1,488,366,495")


if __name__ == "__main__":
    unittest.main()
