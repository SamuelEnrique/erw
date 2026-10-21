"""Session 420 (the Fable run of the night of 20 October 2026): the findings hunt, its files and its page.

Energy Research Warehouse (ERW). warehouse/analysis/findings/hunt_oct20.py and brand_chart.py; docs/findings/2026-10-20/;
/internal/findings and its route /internal/findings/local. No network, no warehouse table: the record and trend tests
run on made-up series (test inputs, never data), and the committed finding folders are read back.

  1. the record test: a record in a recent period passes its four tests; an old record, a thin history, a gap in the
     window and a margin under the floor each fail the test that names it; leading incomplete periods are left out;
  2. the monthly trend keeps the hunt's five tests and writes its words in months;
  3. every committed finding: the seven files, the four states, a caption under 1,300 characters with no em dash that
     ends with the table's name and never names the owner, a do-file to the owner's rules, charts of the two sizes,
     the headline reproduced from extract.csv by the do-file's Python mirror, public tables only, no blocked grid;
  4. the site: the bundler, the type, the trace, the gated route and the page name the four states and the files.

    python -m unittest tests.test_session420 -v
"""

import json
import os
import re
import struct
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIND = os.path.join(ROOT, "warehouse", "analysis", "findings")
sys.path.insert(0, FIND)
import hunt_oct20 as H  # noqa: E402

DAY_DIR = os.path.join(ROOT, "docs", "findings", "2026-10-20")
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def series(values, first=2015, n=35040, complete=None):
    out = [{"period": first + i, "value": v, "n": n, "share": 1.0, "complete": True} for i, v in enumerate(values)]
    for i in complete or []:
        out[i]["complete"] = False
        out[i]["share"] = 0.5
    return out


class TheRecordTest(unittest.TestCase):
    def test_a_recent_record_passes(self):
        r = H.test_record(series([1, 2, 3, 2, 4, 3, 5, 6, 4, 8]), "year", high=True)
        self.assertTrue(r["passed"])
        self.assertEqual((r["period"], r["previous_period"], r["value"], r["previous"]), (2024, 2022, 8, 6))
        self.assertEqual([t["name"] for t in r["tests"]], ["history long enough", "the record period is complete", "no gap in the window", "a margin over the previous record"])

    def test_an_old_record_is_no_claim(self):
        self.assertIsNone(H.test_record(series([1, 9, 3, 2, 4, 3, 5, 6, 4, 8]), "year", high=True))
        # unless the period that holds it is named as recent
        r = H.test_record(series([1, 9, 3, 2, 4, 3, 5, 6, 4, 8]), "year", high=True, recent=[2016])
        self.assertEqual(r["period"], 2016)
        self.assertFalse(r["tests"][0]["passed"])   # one year of history before it

    def test_a_low_record(self):
        r = H.test_record(series([5, 4, 6, 3, 4, 2, 3, 1]), "year", high=False)
        self.assertTrue(r["passed"])
        self.assertEqual((r["direction"], r["previous"]), ("low", 2))

    def test_thin_history_gap_and_margin_each_fail_their_test(self):
        thin = H.test_record(series([1, 2, 3, 4]), "year", high=True)
        self.assertFalse(thin["tests"][0]["passed"])
        gap = H.test_record(series([1, 2, 3, 2, 4, 3, 5, 6, 4, 8], complete=[4]), "year", high=True)
        self.assertFalse(gap["tests"][2]["passed"])
        self.assertIn("2019", gap["tests"][2]["words"])
        close = H.test_record(series([1, 2, 3, 2, 4, 3, 5, 6, 4, 6.1]), "year", high=True)
        self.assertFalse(close["tests"][3]["passed"])

    def test_leading_incomplete_periods_are_not_a_gap(self):
        r = H.test_record(series([0.1, 1, 2, 3, 2, 4, 3, 5, 6, 4, 8], complete=[0]), "year", high=True)
        self.assertTrue(r["passed"])
        self.assertIn("from 2016", r["tests"][2]["words"])

    def test_recent_months(self):
        s = [{"period": f"2025-{m:02d}", "value": m, "n": 30, "complete": True} for m in range(1, 13)] + [{"period": "2026-01", "value": 1, "n": 31, "complete": True}]
        self.assertEqual(H.recent_months(s), [f"2025-{m:02d}" for m in range(2, 13)] + ["2026-01"])


class TheMonthlyTrend(unittest.TestCase):
    def test_five_tests_in_months(self):
        s = [{"period": f"2025-{m:02d}", "value": 40 + m * 3, "n": 30} for m in range(1, 13)]
        c = H.test_trend_months(s, 28, 1, "percent", "2026-01")
        self.assertTrue(c["passed"])
        self.assertEqual((c["first_year"], c["last_year"], c["grain"]), ("2025-01", "2025-12", "month"))
        self.assertEqual(len(c["tests"]), 5)
        for t in c["tests"]:
            self.assertNotIn("year", t["words"])
            self.assertNotRegex(t["words"], r"\b20\d{4}\b")


class TheCommittedFindings(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(DAY_DIR, "index.json"), encoding="utf-8") as f:
            cls.index = json.load(f)
        cls.records = []
        for x in cls.index["findings"]:
            with open(os.path.join(DAY_DIR, x["slug"], "finding.json"), encoding="utf-8") as f:
                cls.records.append(json.load(f))

    def test_ten_findings_with_their_files(self):
        self.assertEqual(len(self.records), 10)
        for r in self.records:
            folder = os.path.join(DAY_DIR, r["slug"])
            for name in ("finding.json", "extract.csv", "series.csv", "check.do", "caption.md", "chart_square.png", "chart_wide.png"):
                self.assertTrue(os.path.isfile(os.path.join(folder, name)), f"{r['slug']}: {name}")
            self.assertIn(r["state"], H.STATES)
            self.assertFalse(r["internal"])
            self.assertEqual(r["license"], "public")
            self.assertNotIn(r["grid"], ("isone", "miso", "nyiso", "spp"))
            self.assertTrue(all(t["passed"] for t in r["tests"]), r["slug"])

    def test_the_caption(self):
        for r in self.records:
            cap = src("docs", "findings", "2026-10-20", r["slug"], "caption.md").strip()
            self.assertEqual(cap, r["caption"])
            self.assertLessEqual(len(cap), 1300, r["slug"])
            self.assertNotIn(EM, cap)
            self.assertTrue(cap.endswith(f"ERW table: {r['tables'][0]}."), r["slug"])
            self.assertNotIn("Samuel", cap)
            self.assertNotIn("Source: ", cap.split("Source:")[0])

    def test_the_do_file_to_the_owners_rules(self):
        for r in self.records:
            do = src("docs", "findings", "2026-10-20", r["slug"], "check.do")
            self.assertNotIn("///", do)
            self.assertNotIn("/*", do)
            self.assertIn(f"Expected headline value: {r['headline']['expected_in_do_file']:.6f}", do)
            self.assertIn('import delimited "extract.csv"', do)
            lines = do.split("\n")
            # one empty line between commands: no two empty lines in a row, and no two commands without one between
            for i in range(1, len(lines) - 1):
                if lines[i] == "":
                    self.assertNotEqual(lines[i + 1], "", f"{r['slug']}: two empty lines at {i}")
                elif lines[i + 1] not in ("",) and i + 1 < len(lines) - 1:
                    self.fail(f"{r['slug']}: commands without an empty line between them at {i}: {lines[i]!r}")
            self.assertIn("destring value, replace force", do)
            self.assertNotIn("Samuel", do)

    def test_the_charts_are_the_two_sizes(self):
        for r in self.records:
            for name, size in (("chart_square.png", (1200, 1200)), ("chart_wide.png", (1600, 900))):
                with open(os.path.join(DAY_DIR, r["slug"], name), "rb") as f:
                    head = f.read(24)
                self.assertEqual(head[:8], b"\x89PNG\r\n\x1a\n")
                self.assertEqual(struct.unpack(">II", head[16:24]), size, f"{r['slug']}: {name}")

    def test_the_headline_is_reproduced_from_the_extract(self):
        self.assertEqual(H.check(DAY_DIR, log=lambda *a: None), 0)

    def test_the_index_agrees(self):
        self.assertEqual([x["slug"] for x in self.index["findings"]], [r["slug"] for r in self.records])
        self.assertEqual([x["state"] for x in self.index["findings"]], [r["state"] for r in self.records])
        self.assertEqual(self.index["summary"]["kept"], 10)
        self.assertGreaterEqual(self.index["summary"]["candidates"], self.index["summary"]["passing"])

    def test_nothing_names_the_owner(self):
        for r in self.records:
            text = json.dumps(r)
            self.assertNotIn("Samuel", text, r["slug"])


class TheSite(unittest.TestCase):
    def test_the_bundler_the_type_the_trace(self):
        self.assertIn("findings_review", src("site", "scripts", "build-content.mjs"))
        self.assertIn('path.join(docs, "findings")', src("site", "scripts", "build-content.mjs"))
        self.assertIn("findings_review?:", src("site", "lib", "markdown.ts"))
        self.assertIn('"/internal/findings/local": ["./content/findings/**/*"]', src("site", "next.config.ts"))
        self.assertIn("/content/findings/", src("site", ".gitignore"))

    def test_the_route_is_gated_and_names_the_files(self):
        route = src("site", "app", "internal", "findings", "local", "route.ts")
        self.assertIn("internalOk(req.cookies.get(COOKIE)?.value)", route)
        for name in ("extract.csv", "check.do", "caption.md", "chart_square.png", "chart_wide.png", "finding.json", "series.csv"):
            self.assertIn(f'"{name}"', route)
        self.assertNotIn("supabase", route.lower())

    def test_the_page_shows_the_four_states(self):
        page = src("site", "components", "analysis", "HuntReview.tsx")
        for s in ("new", "approved", "rejected", "stata_checked"):
            self.assertIn(f'"{s}"', page)
        self.assertIn("Stata checked", page)
        self.assertIn("<HuntReview />", src("site", "app", "internal", "findings", "page.tsx"))
        for name in ("extract.csv", "check.do"):
            self.assertIn(f'data-hunt-file="{name}"', page)


class NoEmDash(unittest.TestCase):
    def test_the_new_files(self):
        for parts in (("warehouse", "analysis", "findings", "hunt_oct20.py"), ("warehouse", "analysis", "findings", "brand_chart.py"),
                      ("site", "components", "analysis", "HuntReview.tsx"), ("site", "app", "internal", "findings", "local", "route.ts"),
                      ("docs", "roundup", "drafts", "2026-W43.md"), ("tests", "test_session420.py")):
            self.assertNotIn(EM, src(*parts), parts)


if __name__ == "__main__":
    unittest.main()
