"""Session 175: FRED through its public CSV endpoint in the Thesis Builder's series module. What is held to: the FRED
entries declare the contract and are in the catalog; a fredgraph.csv answer is parsed as published (a "." left out,
every other value kept, the header checked against the series asked for, another series refused); FRED's robots file as
read on 10 October 2026 allows the CSV path and disallows the PNG; the source line and the browse address are FRED's
citation form; Census and BLS stay left, with the reasons; the method note quotes the terms. No request and no model
call is made here; the environment is read, never set."""
import os
import sys
import unittest
import urllib.robotparser

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "thesis"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import series as SR  # noqa: E402

FX = os.path.join(ROOT, "tests", "fixtures", "session175")
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheCatalog(unittest.TestCase):
    def test_fred_entries_are_in_the_outside_catalog(self):
        fred = [e for e in SR.OUTSIDE if e["source"] == "FRED"]
        self.assertGreaterEqual(len(fred), 15)
        for e in fred:
            self.assertEqual(e["id"], "fred:" + e["series"])
            self.assertTrue(e["title"] and e["unit"] and e["freq"] == "monthly", e["id"])
        ids = [e["id"] for e in SR.OUTSIDE]
        self.assertEqual(len(ids), len(set(ids)), "an id is used twice")
        self.assertIn("fred:MHHNGSP", SR.BY_ID)

    def test_census_and_bls_stay_left_and_fred_does_not(self):
        self.assertEqual(set(SR.LEFT), {"BLS", "Census"})
        self.assertIn("missing_key.html", SR.LEFT["Census"])
        self.assertIn("key_signup", SR.LEFT["Census"])
        self.assertIn("disallows every path", SR.LEFT["BLS"])
        self.assertEqual(SR.FRED_CSV, "https://fred.stlouisfed.org/graph/fredgraph.csv?id=")


class TheParse(unittest.TestCase):
    def test_the_saved_answer_is_parsed_as_published(self):
        with open(os.path.join(FX, "fredgraph_MHHNGSP.csv"), "rb") as f:
            body = f.read()
        pts = SR.parse_fredgraph(body, "MHHNGSP")
        self.assertEqual(pts[0], ("1997-01-01", 3.45))
        self.assertEqual(pts[-1], ("2026-09-01", 2.95))
        self.assertEqual(len(pts), 357)
        self.assertTrue(all(v is not None for _, v in pts))

    def test_a_dot_is_left_out_and_another_series_is_refused(self):
        body = b"observation_date,MHHNGSP\n2020-01-01,2.02\n2020-02-01,.\n2020-03-01,1.79\n"
        self.assertEqual(SR.parse_fredgraph(body, "MHHNGSP"), [("2020-01-01", 2.02), ("2020-03-01", 1.79)])
        with self.assertRaises(RuntimeError):
            SR.parse_fredgraph(body, "DCOILWTICO")
        with self.assertRaises(RuntimeError):
            SR.parse_fredgraph(b"<html>Request Rejected</html>", "MHHNGSP")
        with self.assertRaises(RuntimeError):
            SR.parse_fredgraph(b"observation_date,MHHNGSP\nnot a date,2\n", "MHHNGSP")

    def test_the_pull_cuts_a_long_series_to_its_latest_points(self):
        self.assertEqual(SR.MAX_POINTS, 240)


class TheRobotsFile(unittest.TestCase):
    def test_freds_file_as_read_allows_the_csv_and_not_the_png(self):
        rp = urllib.robotparser.RobotFileParser()
        rp.parse(src("tests", "fixtures", "session175", "fred_robots.txt").splitlines())
        self.assertTrue(rp.can_fetch("*", SR.FRED_CSV + "MHHNGSP"))
        self.assertFalse(rp.can_fetch("*", "https://fred.stlouisfed.org/graph/fredgraph.png?id=MHHNGSP"))
        self.assertFalse(rp.can_fetch("*", "https://fred.stlouisfed.org/searchresults?st=gas"))
        self.assertGreaterEqual(SR.HOST_GAP, 1.0, "FRED's Crawl-delay is 1")


class TheCitation(unittest.TestCase):
    def test_the_source_line_and_the_browse_address_are_freds_form(self):
        import run as R
        s = {"source": "FRED", "id": "fred:MHHNGSP", "title": "Henry Hub Natural Gas Spot Price", "url": SR.FRED_CSV + "MHHNGSP", "retrieved": "2026-10-10"}
        self.assertEqual(R.browse_url(s), "https://fred.stlouisfed.org/series/MHHNGSP")
        line = R.series_line(s)
        self.assertTrue(line.startswith("Source: Henry Hub Natural Gas Spot Price [MHHNGSP], retrieved from FRED, Federal Reserve Bank of St. Louis; https://fred.stlouisfed.org/series/MHHNGSP, "), line)
        self.assertTrue(line.endswith("."))


class TheDocuments(unittest.TestCase):
    def test_the_method_note_quotes_the_terms(self):
        m = src("docs", "methods", "thesis.md")
        for words in ("fredgraph.csv", "non-commercial, educational, and personal uses", "excessive, disruptive", "Crawl-delay 1",
                      "missing_key.html", "retrieved from FRED, Federal Reserve Bank of St. Louis"):
            self.assertIn(words, m, words)

    def test_no_em_dash_in_this_sessions_files(self):
        for rel in ("warehouse/thesis/series.py", "warehouse/thesis/run.py", "tests/test_session175.py", "docs/methods/thesis.md"):
            self.assertNotIn(EM, src(*rel.split("/")), rel)


if __name__ == "__main__":
    unittest.main()
