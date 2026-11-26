"""Session 8613 (chain 504, 19 November 2026): a second reader's read of the region tabs on the real files.

Energy Research Warehouse (ERW). Five more cases were taken in a browser on a build, on the controls the first read
did not exercise (docs/reviews/grid-map-read-2026-11-19.md, rows 39 on). What is held here:
- row 39: the trade tab offered the newest thirteen months and no way to an older one, though a region's trade file
  goes back to July 2018. Every year the file holds is now a chip, and the months offered are those of the year shown;
- row 40: with a whole year as the period, the shares said "301 days held" and not of which months. The line now gives
  the file's own count of the year's months held and due, and names the months not held.
The figures below are made up for the tests and are in no page. Nothing here sets the environment or makes a request.
"""

import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
EM = chr(0x2014)


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def node(code):
    r = subprocess.run([NODE, "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


@unittest.skipUnless(NODE, "node is not installed")
class TheYearsOfATradeFile(unittest.TestCase):
    """Row 39."""

    @classmethod
    def setUpClass(cls):
        cls.d = node("import { tradeYears } from './lib/gridregions.ts';"
                     "const months = ['2024-11', '2024-12', '2025-01', '2025-02', '2025-03', '2026-01'];"
                     "const n = (own) => ({ net_imports_mwh: own, their_report_mwh: own, gap_mwh: own, hours_own: own, hours_their: own, hours_both: own });"
                     # A reports in every month but March 2025; B only in December 2024 and March 2025; nobody in January 2026
                     "const file = { months, net_imports_mwh: [1, 1, 1, 1, 1, null], neighbors: { A: n([5, 6, 7, 8, null, null]), B: n([null, 9, null, null, 3, null]) } };"
                     "console.log(JSON.stringify({ years: tradeYears(file), none: tradeYears({ months, net_imports_mwh: [], neighbors: { A: n([null, null, null, null, null, null]) } }), empty: tradeYears({ months: [], net_imports_mwh: [], neighbors: {} }) }));")

    def test_every_year_newest_first_with_its_months_newest_first(self):
        self.assertEqual(self.d["years"], [{"year": "2025", "months": ["2025-03", "2025-02", "2025-01"]}, {"year": "2024", "months": ["2024-12", "2024-11"]}])

    def test_a_month_no_neighbour_reported_by_the_regions_own_side_is_not_offered(self):
        self.assertNotIn("2026", [y["year"] for y in self.d["years"]])     # January 2026 holds no own report, so the year has no month to show
        self.assertEqual(self.d["none"], [])
        self.assertEqual(self.d["empty"], [])

    def test_the_tab_offers_the_years_and_the_months_of_the_year_shown(self):
        v = src("site", "components", "grid", "RegionViews.tsx")
        self.assertIn("const years = tradeYears(trade);", v)
        self.assertIn('<Chips label="Month" items={(years.find((y) => y.year === (asked ?? "").slice(0, 4))?.months ?? []).map(', v)
        self.assertIn('<Chips label="Year" items={years.map((y) => ({ key: y.year, label: y.year, href: regionHref(code, "gravity", { month: y.months[0] === newest ? undefined : y.months[0] })', v)
        self.assertNotIn("trade.months.slice(-13)", v)


@unittest.skipUnless(NODE, "node is not installed")
class AYearsOwnMonths(unittest.TestCase):
    """Row 40."""

    @classmethod
    def setUpClass(cls):
        cls.d = node("import { yearMonths } from './lib/gridregions.ts';"
                     "console.log(JSON.stringify({ whole: yearMonths({ months: 12, months_due: 12, missing: [], days_held: 365 }), part: yearMonths({ months: 10, months_due: 12, missing: ['2025-01', '2025-02', 7], days_held: 301 }),"
                     " running: yearMonths({ months: 10, months_due: 11, missing: ['2026-11'] }), month: yearMonths({ days_held: 31, days_in_month: 31 }), nothing: yearMonths(null), words: yearMonths({ months: 'ten', months_due: 12 }) }));")

    def test_the_files_own_count_and_the_months_not_held(self):
        self.assertEqual(self.d["whole"], {"months": 12, "due": 12, "missing": []})
        self.assertEqual(self.d["part"], {"months": 10, "due": 12, "missing": ["2025-01", "2025-02"]})   # what is no month's name is left out
        self.assertEqual(self.d["running"], {"months": 10, "due": 11, "missing": ["2026-11"]})

    def test_a_month_or_an_entry_that_does_not_say_gives_nothing(self):
        self.assertIsNone(self.d["month"])
        self.assertIsNone(self.d["nothing"])
        self.assertIsNone(self.d["words"])

    def test_the_line_under_the_shares(self):
        v = src("site", "components", "grid", "RegionViews.tsx")
        self.assertIn("const ofYear = asked && asked.length === 4 ? yearMonths(mixFile.years[asked]) : null;", v)
        self.assertIn("data-year-months={`${ofYear.months} of ${ofYear.due}`}", v)
        self.assertIn('{ofYear.due === 12 ? "" : " so far"}', v)
        self.assertIn("(not held: {ofYear.missing.map((k) => mix.periodName(k)).join(\", \")})", v)


class TheReplicationKnowsARebuiltFile(unittest.TestCase):
    """The data machine rebuilt the mix files on 19 November without rebuilding the index: the index's stamp did not
    move, and the replication compared a stale read of the page with the new files (403 figures not met). The page read
    now keeps when each region's two files were built, and the comparison stops when one has changed."""

    def test_the_read_keeps_each_files_stamp(self):
        s = src("replication", "grid", "regions_figures.mjs")
        self.assertIn("index_built: index.built, files_built: filesBuilt(), regions }", s)
        with open(os.path.join(ROOT, "replication", "grid", "regions_page_figures.json"), encoding="utf-8") as f:
            page = json.load(f)
        self.assertEqual(len(page["files_built"]), 13)
        self.assertTrue(all(v["mix"] and v["trade"] for v in page["files_built"].values()))

    def test_a_file_rebuilt_since_the_read_stops_the_comparison(self):
        import contextlib
        import importlib.util
        import io
        import tempfile
        spec = importlib.util.spec_from_file_location("replicate_regions", os.path.join(ROOT, "replication", "grid", "replicate_regions.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        with open(os.path.join(ROOT, "replication", "grid", "regions_page_figures.json"), encoding="utf-8") as f:
            page = json.load(f)
        # session 10000 (chain 701, part C3): the data machine rebuilds the region files every day, and its push was
        # refused from 21 November because the index's own stamp had moved, which stops the comparison earlier and with
        # other words. The test holds the stamp check only where the read and the files agree: the untouched read first
        with contextlib.redirect_stdout(io.StringIO()):
            untouched = m.main([])
        if untouched != 0:
            self.skipTest("the region files on this machine are not the ones the page was read from")
        first = sorted(page["files_built"])[0]
        page["files_built"][first]["mix"] = "2026-11-19T12:02:00Z"          # as if the page had been read before the rebuild
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "stale.json")
            with open(p, "w", encoding="utf-8") as f:
                json.dump(page, f)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = m.main(["--page", p])
        if code == 0:
            self.skipTest("the region files on this machine are not the ones the page was read from")
        self.assertEqual(code, 2)
        self.assertIn("were rebuilt since the page was read", out.getvalue())
        self.assertNotIn("NOT MET", out.getvalue())


class TheRest(unittest.TestCase):
    def test_the_check_follows_a_year(self):
        s = src("site", "scripts", "check-grid-regions.mjs")
        self.assertIn("tradeYears(trade)", s)
        self.assertIn('data-chip="Year:', s)

    def test_no_em_dash(self):
        for p in (("site", "components", "grid", "RegionViews.tsx"), ("site", "lib", "gridregions.ts"), ("site", "scripts", "check-grid-regions.mjs"), ("tests", "test_session8613.py")):
            self.assertNotIn(EM, src(*p), p)


if __name__ == "__main__":
    unittest.main()
