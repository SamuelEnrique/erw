"""Session 10000 (chain 701, part D, after the owner's ruling of 26 November 2026): warehouse/connectors/sec_edgar.py (the
listed energy companies and their filed statements) and the equities page files built from them. Made-up inputs; no
request is made and no table is read."""
import importlib.util
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))


def load(rel, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, *rel.split("/")))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


SE = load("warehouse/connectors/sec_edgar.py", "sec_edgar_t")
EP = load("warehouse/derived/equity_page_files.py", "equity_pages_t")


def fact(start, end, val, accn, filed, form="10-Q", fp="Q3", fy=2026):
    f = {"end": end, "val": val, "accn": accn, "fy": fy, "fp": fp, "form": form, "filed": filed}
    if start:
        f["start"] = start
    return f


class TheContactAndThePace(unittest.TestCase):
    def test_no_contact_no_request(self):
        saved = os.environ.pop("SEC_USER_AGENT", None)
        root = SE.ip.ROOT
        try:
            SE.ip.ROOT = os.path.join(ROOT, "no-such-folder")
            with self.assertRaises(RuntimeError):
                SE.agent()
        finally:
            SE.ip.ROOT = root
            if saved is not None:
                os.environ["SEC_USER_AGENT"] = saved

    def test_under_the_secs_rate_and_no_address_in_the_code(self):
        self.assertGreaterEqual(SE.WAIT, 0.1)   # ten a second is the SEC's limit; this waits a quarter of a second
        with open(os.path.join(ROOT, "warehouse", "connectors", "sec_edgar.py"), encoding="utf-8") as f:
            s = f.read()
        self.assertNotIn("stanford.edu", s)      # the contact address lives in .env, never in the repository
        self.assertNotIn("/cgi-bin", s.split('"""', 2)[2])   # www.sec.gov's robots file disallows it


class TheUniverse(unittest.TestCase):
    def test_only_exchange_listed_and_one_row_a_company(self):
        t = {"fields": ["cik", "name", "ticker", "exchange"],
             "data": [[1, "A CORP", "AAA", "NYSE"], [1, "A CORP", "AAB", "NYSE"], [2, "B CO", "BBB", "OTC"], [3, "C INC", "CCC", "Nasdaq"]]}
        lst = SE.listed(t)
        self.assertEqual(sorted(lst), ["0000000001", "0000000003"])
        self.assertEqual(lst["0000000001"][1], ["AAA", "AAB"])

    def test_the_written_rule(self):
        self.assertEqual(SE.segments_of("1311"), (["exploration_production"], None))
        segs, note = SE.segments_of("2911")
        self.assertEqual(segs, ["integrated_oil_gas", "refining"])
        self.assertIn("in both", note)
        self.assertEqual(SE.segments_of("3674"), ([], None))   # all semiconductors: not a solar code
        self.assertEqual(SE.segments_of("3690"), ([], None))
        for s, segs in SE.SIC_SEGMENTS.items():
            self.assertEqual(len(segs) > 1, s in SE.TWO_NOTE, s)

    def test_every_segment_has_a_rule_or_a_reason(self):
        placed = {s for v in SE.SIC_SEGMENTS.values() for s in v}
        for i, _ in EP.SEGMENTS:
            self.assertTrue((i in placed) == (i in EP.SEG_RULE), i)
            self.assertTrue((i in placed) != (i in EP.NO_CODE), i)
        self.assertEqual(set(SE.NO_CODE), set(EP.NO_CODE))

    def test_the_name_match_is_exact_but_for_case_commas_and_periods(self):
        self.assertEqual(SE.norm_name("NextEra Energy, Inc."), SE.norm_name("NEXTERA ENERGY INC"))
        self.assertNotEqual(SE.norm_name("NextEra Energy Partners"), SE.norm_name("NEXTERA ENERGY INC"))


class TheStatements(unittest.TestCase):
    def facts(self):
        return {"facts": {"us-gaap": {
            "Revenues": {"units": {"USD": [fact("2026-07-01", "2026-09-30", 100, "a-1", "2026-11-02"),
                                           fact("2026-01-01", "2026-09-30", 300, "a-1", "2026-11-02"),
                                           fact("2026-01-01", "2026-12-31", 999, "a-0", "2026-05-01", fp="Q1")]}},
            "RevenueFromContractWithCustomerExcludingAssessedTax": {"units": {"USD": [
                fact("2026-07-01", "2026-09-30", 98, "a-1", "2026-11-02"),
                fact("2025-07-01", "2025-09-30", 90, "a-2", "2025-11-01")]}},
            "LongTermDebtNoncurrent": {"units": {"USD": [fact(None, "2026-09-30", 50, "a-1", "2026-11-02")]}},
            "CommonStockSharesOutstanding": {"units": {"shares": [fact(None, "2026-09-30", 7, "a-1", "2026-11-02")]}},
            "NetIncomeLoss": {"units": {"USD": [fact("2026-07-01", "2026-09-30", 10, "a-1", "2026-11-02", form="8-K")]}},
        }}}

    def test_lines_periods_and_concepts(self):
        t = SE.fundamentals_rows("0000000001", "AAA", self.facts(), "2026-11-27T00:00:00Z")
        got = {(r.variable, r.ts_utc[:10], r.x_accession): (r.value, r.x_concept) for r in t.itertuples()}
        self.assertEqual(got[("revenue_3m_usd", "2026-09-30", "a-1")], ("100", "us-gaap:Revenues"))   # the first concept wins
        self.assertEqual(got[("revenue_9m_usd", "2026-09-30", "a-1")], ("300", "us-gaap:Revenues"))
        self.assertEqual(got[("revenue_3m_usd", "2025-09-30", "a-2")][1], "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax")
        self.assertEqual(got[("long_term_debt_usd", "2026-09-30", "a-1")], ("50", "us-gaap:LongTermDebtNoncurrent"))
        self.assertEqual(t[t.variable == "shares_outstanding"]["unit"].tolist(), ["count"])
        self.assertFalse(any(r.ts_utc.startswith("2026-12-31") for r in t.itertuples()))   # ends after its filing: left out
        self.assertFalse(any(v.startswith("net_income") for v in t.variable))               # an 8-K is not read
        self.assertFalse(t.duplicated(["entity", "variable", "ts_utc", "vintage"]).any())
        self.assertEqual(list(t.columns), SE.FUND_COLS)

    def test_the_page_reads_each_filings_own_period(self):
        t = SE.fundamentals_rows("0000000001", "AAA", self.facts(), "2026-11-27T00:00:00Z")
        rows, concepts = EP.quarterly(t)
        cols = EP.QCOLS
        first = dict(zip(cols, rows[0]))
        self.assertEqual((first["period_end"], first["filed"]), ("2026-09-30", "2026-11-02"))
        self.assertEqual(sorted(dict(zip(cols, r))["months"] for r in rows if dict(zip(cols, r))["accession"] == "a-1"), [3, 9])
        self.assertEqual((first["debt"], first["shares_outstanding"]), (50, 7))
        self.assertEqual(concepts["revenue"], "us-gaap:Revenues")


class TheDailySteps(unittest.TestCase):
    def test_the_universe_and_statements_before_the_pages(self):
        with open(os.path.join(ROOT, "warehouse", "run_data_machine.sh"), encoding="utf-8") as f:
            s = f.read()
        u, fu = s.index("soft_step dm_sec_universe "), s.index("soft_step dm_sec_fundamentals ")
        self.assertLess(u, fu)
        self.assertLess(fu, s.index("soft_step dm_equity_pages "))


if __name__ == "__main__":
    unittest.main()
