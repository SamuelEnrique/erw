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


class TheDailyIndexes(unittest.TestCase):
    """The last index day read is the last day whose index answered: a holiday before it is passed, a day not yet
    published after it is asked again by the next run."""

    def client(self, answers):
        class R:
            def __init__(self, code, text=""):
                self.status_code, self.text = code, text

        class C:
            def get(_, url):
                d = url.rsplit(".", 2)[-2]
                code, text = answers.get(d, (404, ""))
                return R(code, text)
        return C()

    def test_a_holiday_is_passed_and_an_unpublished_day_kept(self):
        import datetime as dt
        line = ("10-Q        SOME ENERGY CO                                                1234567     20261125    "
                "edgar/data/1234567/0001234567-26-000001.txt" + chr(10) +
                "10-Q        ITS UTILITY CO                                                7654321     20261125    "
                "edgar/data/7654321/0001234567-26-000001.txt")
        answers = {"20261125": (200, line), "20261126": (404, ""), "20261127": (200, ""), "20261130": (404, "")}
        out, last, by_accn = SE.filers_since(self.client(answers), dt.date(2026, 11, 24), dt.date(2026, 11, 30), lambda m: None)
        self.assertEqual(out, {"0001234567", "0007654321"})
        self.assertEqual(by_accn["0001234567-26-000001"], {"0001234567", "0007654321"})   # a joint filing under each filer
        self.assertEqual(SE.coregistrants(None, "0001234567", "0001234567-26-000001", by_accn, lambda m: None), ["0007654321"])
        self.assertEqual(last, dt.date(2026, 11, 27))   # Thanksgiving (26th) passed; the 30th not yet published

    def test_nothing_published_keeps_the_day(self):
        import datetime as dt
        out, last, _ = SE.filers_since(self.client({}), dt.date(2026, 11, 26), dt.date(2026, 11, 27), lambda m: None)
        self.assertEqual((out, last), (set(), dt.date(2026, 11, 26)))


class AJointFiling(unittest.TestCase):
    """Done-line request 579 (1): a company's filing whose facts the SEC keeps in a co-registrant's file is read from
    there, that filing's facts only."""

    def test_only_the_filings_own_facts(self):
        facts = {"facts": {"us-gaap": {"Revenues": {"units": {"USD": [
            fact("2026-04-01", "2026-06-30", 7534, "p-26-60", "2026-07-24", fp="Q2"),
            fact("2026-04-01", "2026-06-30", 4000, "s-26-01", "2026-07-24", fp="Q2")]}}}}}
        t = SE.fundamentals_rows("0000753308", "NEE", facts, "2026-11-27T00:00:00Z", only_accns={"p-26-60"})
        self.assertEqual((len(t), t["value"].iloc[0], t["entity"].iloc[0]), (1, "7534", "sec:0000753308"))

    def test_a_parents_file_is_never_a_subsidiarys(self):
        self.assertTrue(SE.same_entity("NEXTERA ENERGY, INC.", "NEXTERA ENERGY INC"))
        self.assertTrue(SE.same_entity("AMERICAN ELECTRIC POWER CO INC.", "American Electric Power Company, Inc."))
        self.assertFalse(SE.same_entity("SOUTHERN CO", "GEORGIA POWER CO"))   # Southern's file holds Southern's figures
        self.assertFalse(SE.same_entity("", ""))

    def test_the_companys_own_filings_from_the_bulk_file(self):
        import io as _io
        import json as _json
        import zipfile as _zip
        buf = _io.BytesIO()
        with _zip.ZipFile(buf, "w") as z:
            z.writestr("CIK0000753308.json", _json.dumps({"filings": {"recent": {
                "form": ["10-Q", "8-K", "10-Q"], "accessionNumber": ["a1", "a2", "a3"], "reportDate": ["2026-09-30", "", "2026-06-30"],
                "isXBRL": [1, 0, 0]}}}))
        z = _zip.ZipFile(buf)
        self.assertEqual(SE.own_filings("0000753308", z), {"a1": "2026-09-30"})   # a 10-Q marked XBRL only
        self.assertEqual(SE.own_filings("0000000001", z), {})


class TheNewestFiled(unittest.TestCase):
    """Done-line request 578: index.json's newest_filed, by the page's newestOf rule; and request 579's notes."""

    def row(self, start, end, months, filed, accn, rev=None, ni=None, debt=None):
        r = dict.fromkeys(EP.QCOLS)
        r.update(period_start=start, period_end=end, months=months, form="10-Q", filed=filed, accession=accn, url="u-" + accn,
                 revenue=rev, net_income=ni, debt=debt)
        return [r[c] for c in EP.QCOLS]

    def test_the_shortest_period_and_the_later_filing(self):
        q = [self.row("2026-07-01", "2026-09-30", 3, "2026-11-02", "a2", rev=100),
             self.row("2026-01-01", "2026-09-30", 9, "2026-11-02", "a2", rev=300, ni=30, debt=50),
             self.row("2026-04-01", "2026-06-30", 3, "2026-08-01", "a1", rev=90)]
        n = EP.newest_filed(q)
        self.assertEqual((n["period_end"], n["filed"], n["url"]), ("2026-09-30", "2026-11-02", "u-a2"))
        self.assertEqual(n["revenue"], {"months": 3, "v": 100})
        self.assertEqual(n["net_income"], {"months": 9, "v": 30})   # only the year to date was filed
        self.assertEqual((n["capex"], n["debt"]), (None, 50))
        self.assertIsNone(EP.newest_filed([]))

    def test_a_filer_that_stopped_and_a_new_registrant(self):
        old = [self.row("2016-07-01", "2016-09-30", 3, "2016-11-14", "r1", rev=5)]
        self.assertIn("filed neither since", EP.shown_why(old, "2026-11-27T00:00:00Z"))
        new = [self.row("2026-04-01", "2026-06-30", 3, "2026-08-01", "x1", rev=5)]
        self.assertIn("a new registrant", EP.shown_why(new, "2026-11-27T00:00:00Z"))
        both = old + new
        self.assertIsNone(EP.shown_why(both, "2026-11-27T00:00:00Z"))


class TheBoardsHeldRows(unittest.TestCase):
    def test_a_held_row_carries_no_heat_rate(self):
        with open(os.path.join(ROOT, "warehouse", "derived", "board_page.py"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn('if ref and r.get("status") == "ok":', s)


class AUtilitysRevenue(unittest.TestCase):
    def test_the_total_before_the_contracts_part(self):
        # the cross-check of 27 November 2026: for NextEra and Duke the contracts concept is a part of operating revenue
        order = SE.CONCEPTS["revenue_usd"][2]
        self.assertLess(order.index("RegulatedAndUnregulatedOperatingRevenue"),
                        order.index("RevenueFromContractWithCustomerExcludingAssessedTax"))
        self.assertEqual(order[0], "Revenues")


class TheDailySteps(unittest.TestCase):
    def test_the_universe_and_statements_before_the_pages(self):
        with open(os.path.join(ROOT, "warehouse", "run_data_machine.sh"), encoding="utf-8") as f:
            s = f.read()
        u, fu = s.index("soft_step dm_sec_universe "), s.index("soft_step dm_sec_fundamentals ")
        self.assertLess(u, fu)
        self.assertLess(fu, s.index("soft_step dm_equity_pages "))


if __name__ == "__main__":
    unittest.main()
