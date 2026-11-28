"""Ready branch for /forecast (session 11408, chain 770 part C; weekend page 2026-11-28, part 3.5, the operator's filing
check: "a sentence where no month is flagged: none (as built), or one"). Not the default: it waits for Samuel's ruling.

The other choice: where no month is flagged, one sentence says so above the months' fold (FilingCheck in
site/app/forecast/lines.tsx). On the files now on main: 20 of the 64 places flag no month; on main none of them draws a
sentence, here all 20. site/scripts/test-forecast-lines.mjs is turned to the same rule (it runs under
tests/test_session10409_forecast_lines.py)."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class ASentenceWhereNoMonthIsFlagged(unittest.TestCase):
    def test_the_sentence(self):
        lines = src("site", "app", "forecast", "lines.tsx")
        self.assertIn("{flagged === 0 ? (", lines)
        self.assertIn("data-fc-filing-none-flagged={k}>In none of the", lines)
        self.assertIn("months held is the forecast filed on Form EIA-930 more than {tol ?? 5} percent from the demand it forecasts over the whole month.", lines)
        self.assertIn("ready branch wip/ready-forecast-filing-none-sentence", src("site", "scripts", "test-forecast-lines.mjs"))
        self.assertIn("Where no month is flagged, `/forecast` says so in one", src("docs", "methods", "predict.md"))

    def test_places_it_applies_to(self):
        d = os.path.join(ROOT, "site", "data", "predict")
        idx = json.load(open(os.path.join(d, "index.json"), encoding="utf-8"))
        none = 0
        for p in idx["places"]:
            path = os.path.join(d, f"{p['place']}.json")
            if os.path.exists(path):
                f = ((json.load(open(path, encoding="utf-8")).get("series") or {}).get("demand") or {}).get("operator_filing") or {}
                none += f.get("months_flagged") == 0
        self.assertGreater(none, 0)


if __name__ == "__main__":
    unittest.main()
