"""Session 10406 (chain 720, part E): the separate line "with the weather known" on /forecast.

Window B's files hold it for every place since their build of 26 November 2026, 14:05 UTC (the contract's change of
session 10601): the regression with the target day's own observed temperature added. It is not a forecast. The
contract and the chain ask a page that shows it to label it "with the weather known"; this page gives it a table of
its own under those words, beside the regression and the operator on the same hours, and draws it in no chart and no
other table. The Node test (scripts/test-forecast-peak.mjs, its part 8) draws it from a fixture.

    python -m pytest tests/test_session10406_forecast_weather.py
"""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheLineIsLabelledAndApart(unittest.TestCase):
    def test_the_label_is_the_contracts_words(self):
        lib = src("site", "lib", "predict.ts")
        self.assertIn('export const WEATHER_LABEL = "With the weather known";', lib)
        self.assertIn('export const WEATHER_METHODS = ["with_weather_known", "regression", "operator"] as const;', lib)
        view = src("site", "app", "forecast", "view.tsx")
        self.assertIn("{WEATHER_LABEL}</span> (not a forecast), beside the regression and the operator on the same hours, {mu}</h4>", view)

    def test_it_is_of_demand_in_one_table_and_in_no_chart(self):
        view = src("site", "app", "forecast", "view.tsx")
        self.assertIn('const weathered = s === "demand" && info.some(', view)
        self.assertEqual(view.count('data-fc-weather="1"'), 1)
        # no chart's series and no other table's columns are built from the line
        for name in ("chartSeries", "Tomorrow", "PastDay", "AllPlaces", "DaysAhead"):
            start = view.index(f"function {name}(")
            nxt = re.search(r"\n(export )?function ", view[start + 10:])
            body = view[start:start + 10 + nxt.start()] if nxt else view[start:]
            self.assertNotIn("with_weather_known", body, name)
            self.assertNotIn("WEATHER_", body, name)
        # the four methods every other table sets side by side are as they were
        self.assertIn('export const FOUR = ["erw", "operator", "yesterday", "week_ago"] as const;', src("site", "lib", "predict.ts"))

    def test_the_value_check_knows_its_megawatts(self):
        text = src("site", "scripts", "check-values.mjs")
        rule = re.search(r"const predictWhole = /(.+?)/\.test\(check\)", text).group(1).replace("\\/", "/")
        self.assertRegex("pf|predict/region-tex.json|series/demand/with_weather_known/all/mae/with_weather_known", rule)
        self.assertRegex("pf|predict/region-tex.json|series/demand/with_weather_known/last_2_years/mae/operator", rule)
        self.assertNotRegex("pf|predict/region-tex.json|series/demand/with_weather_known/all/mape/regression", rule)
        self.assertNotRegex("pf|predict/region-tex.json|series/demand/with_weather_known/all/hours", rule)

    def test_the_files_on_the_site_hold_the_shape_the_page_reads(self):
        d = os.path.join(SITE, "data", "predict")
        if not os.path.isfile(os.path.join(d, "index.json")):
            self.skipTest("the forecast's files are not on the site")
        with open(os.path.join(d, "index.json"), encoding="utf-8") as f:
            index = json.load(f)
        if index.get("example"):
            self.skipTest("the files on the site are the contract's examples")
        seen = 0
        for p in index["places"]:
            with open(os.path.join(d, p["file"]), encoding="utf-8") as f:
                w = json.load(f)["series"]["demand"].get("with_weather_known")
            if not w:
                continue
            seen += 1
            for span in ("all", "last_2_years"):
                part = w.get(span)
                if part is None:
                    continue
                for metric in ("mae", "mape"):
                    self.assertTrue(set(part[metric]) <= {"with_weather_known", "regression", "operator"}, p["place"])
                self.assertIn("hours", part, p["place"])
        if not seen:
            self.skipTest("no place's file holds the line yet")

    def test_no_em_dash(self):
        self.assertNotIn(EM, src("tests", "test_session10406_forecast_weather.py").replace("chr(0x2014)", ""))


if __name__ == "__main__":
    unittest.main()
