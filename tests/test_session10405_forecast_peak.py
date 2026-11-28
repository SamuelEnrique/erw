"""Session 10405 (chain 720, part E): the day's peak and the days after tomorrow on /forecast.

Window B's contract gained both on 26 November 2026 (docs/state/page_files_predict.md, the changes of session 10601):
`series.demand.peak` in each place file, and `site/data/predict/ahead.json`. The page draws them as additions: nothing
it drew before is moved, and a page with neither file is the page as it was. The Node test draws the page from a
fixture; this file pins what the site's lists and checks must know of the new route and the new figures.

    python -m pytest tests/test_session10405_forecast_peak.py
"""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
REACT = os.path.isdir(os.path.join(SITE, "node_modules", "react"))
EM = chr(0x2014)
NEW = [("site", "app", "forecast", "ahead", "route.ts"), ("site", "app", "forecast", "ahead", "python", "route.ts"),
       ("site", "app", "forecast", "ahead", "stata", "route.ts"), ("site", "app", "forecast", "ahead", "reader.ts"),
       ("site", "scripts", "test-forecast-peak.mjs")]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheNodeTest(unittest.TestCase):
    @unittest.skipUnless(NODE and REACT, "node or the site's packages are not installed")
    def test_what_a_reader_sees(self):
        r = subprocess.run([NODE, "--import", "./scripts/events-page-register.mjs", "scripts/test-forecast-peak.mjs"],
                           capture_output=True, text=True, cwd=SITE, timeout=600)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])
        self.assertRegex(r.stdout, r"ok: \d+ checks of /forecast's peak and days ahead")


class ThePageAddsAndMovesNothing(unittest.TestCase):
    def test_the_sections_and_the_four_methods_are_as_they_were(self):
        view = src("site", "app", "forecast", "view.tsx")
        for heading in ("Tomorrow", "How it has done", "Every place", "Downloads"):
            self.assertIn(f'<ToolSection title="{heading}"', view)
        self.assertEqual(len(re.findall(r"<ToolSection title=", view)), 4)
        self.assertIn('export const FOUR = ["erw", "operator", "yesterday", "week_ago"] as const;', src("site", "lib", "predict.ts"))

    def test_both_blocks_are_of_demand_and_wait_for_their_files(self):
        view = src("site", "app", "forecast", "view.tsx")
        self.assertIn('{DAYS_AHEAD_SHOWN && q.s === "demand" && ahead ? (', view)  # ready branch wip/ready-forecast-no-days-ahead (session 11408)
        self.assertIn('const ahead = aheadFile && aheadFile.example !== true && index?.example !== true ? aheadFile : null;', view)
        self.assertIn('const peaked = s === "demand" && info.some(', view)

    def test_the_day_the_place_file_draws_is_not_drawn_twice(self):
        lib = src("site", "lib", "predict.ts")
        self.assertIn("(tomorrow ? h.target_day > tomorrow : h.days_after_tomorrow >= 1)", lib)

    def test_no_sorting_by_score_and_no_word_that_ranks(self):
        view = src("site", "app", "forecast", "view.tsx")
        block = view[view.index("function DaysAhead("):view.index("/** A past day for one place")]
        self.assertNotIn(".sort(", block)
        self.assertIsNone(re.search(r"\b(better|worse|best|worst|wins?|loses?|outperform\w*)\b", block.replace("shown only where", ""), re.I))
        # the days are in the calendar's order, set in the library by the day and by nothing else
        self.assertIn(".sort((a, b) => a.h.target_day.localeCompare(b.h.target_day))", src("site", "lib", "predict.ts"))

    def test_nothing_of_the_economic_impact_tool(self):
        for parts in NEW + [("site", "app", "forecast", "view.tsx"), ("site", "lib", "predict.ts"), ("site", "lib", "predictfiles.ts")]:
            self.assertIsNone(re.search(r'from "@/(lib/forecast|data/forecast|app/impact)', src(*parts)), "/".join(parts))


class TheListsAndTheChecks(unittest.TestCase):
    def test_the_route_reads_one_file_and_no_word_of_the_address(self):
        self.assertIn('"/forecast/ahead": ["./data/predict/ahead.json"]', src("site", "next.config.ts"))
        for parts in NEW[:3]:
            text = src(*parts)
            self.assertNotIn("searchParams", text, "/".join(parts))
            self.assertNotIn("node:fs", text, "/".join(parts))
            self.assertIn('new URL("/forecast/ahead", req.url)', text, "/".join(parts))
        self.assertIn('export const predictAhead = () => readPredict<AheadFile>("ahead.json");', src("site", "lib", "predictfiles.ts"))

    def test_the_value_check_knows_the_new_megawatts(self):
        text = src("site", "scripts", "check-values.mjs")
        rule = re.search(r"const predictWhole = /(.+?)/\.test\(check\)", text).group(1).replace("\\/", "/")
        for key in ("pf|predict/region-tex.json|series/demand/peak/last_2_years/methods/erw/mae",
                    "pf|predict/ahead.json|places/28/horizons/2/forecast/17/2",
                    "pf|predict/ahead.json|places/28/horizons/2/last_2_years/mae/regression",
                    "pf|predict/ahead.json|places/28/horizons/2/last_2_years/operator_day_ahead_mae_same_hours",
                    "pf|predict/region-tex.json|series/demand/tomorrow/17/2", "pf|predict/scores.json|rows/7495/6"):
            self.assertRegex(key, rule)
        for key in ("pf|predict/region-tex.json|series/demand/peak/last_2_years/methods/erw/mape",
                    "pf|predict/region-tex.json|series/demand/peak/last_2_years/methods/erw/hour_exact_pct",
                    "pf|predict/region-tex.json|series/demand/peak/last_2_years/days",
                    "pf|predict/ahead.json|places/28/horizons/2/last_2_years/mape/regression",
                    "pf|predict/ahead.json|places/28/horizons/2/band_coverage_pct"):
            self.assertNotRegex(key, rule)

    def test_the_files_on_the_site_hold_what_the_page_reads(self):
        # once window B's files are on the site: every place has a peak, and the file of the days ahead names places
        # the index lists; where they are not there yet, nothing is asserted
        d = os.path.join(SITE, "data", "predict")
        if not os.path.isfile(os.path.join(d, "ahead.json")) or not os.path.isfile(os.path.join(d, "index.json")):
            self.skipTest("the forecast's files are not on the site")
        with open(os.path.join(d, "index.json"), encoding="utf-8") as f:
            index = json.load(f)
        with open(os.path.join(d, "ahead.json"), encoding="utf-8") as f:
            ahead = json.load(f)
        if index.get("example") or ahead.get("example"):
            self.skipTest("the files on the site are the contract's examples")
        listed = {p["place"] for p in index["places"]}
        self.assertTrue(ahead["places"])
        for p in ahead["places"]:
            self.assertIn(p["place"], listed)
            for h in p["horizons"]:
                self.assertEqual(h["forecast_columns"][:5], ["ts_utc", "local_hour", "erw", "lo", "hi"], p["place"])
                self.assertEqual(h["forecast"] is not None, bool(h["shown"]), p["place"])

    def test_no_em_dash(self):
        for parts in NEW:
            self.assertNotIn(EM, src(*parts), "/".join(parts))
        self.assertNotIn(EM, src("tests", "test_session10405_forecast_peak.py").replace("chr(0x2014)", ""))


if __name__ == "__main__":
    unittest.main()
