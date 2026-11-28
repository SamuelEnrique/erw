"""Ready branch for /forecast (session 11408, chain 770 part C; weekend page 2026-11-28, part 3.5, the operator's filing
check: "lead with the filing as published (as built), or with the sound months"). Not the default: it waits for
Samuel's ruling.

The other choice, read as its smallest form: where the filing breaks (44 of the 64 places on the files now on main flag
a month), the check's table leads with the scores on the months that pass and puts every month second (FilingCheck in
site/app/forecast/lines.tsx). No figure moves; the report card is unchanged. site/scripts/test-forecast-lines.mjs checks
the order (it runs under tests/test_session10409_forecast_lines.py)."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheMonthsThatPassLead(unittest.TestCase):
    def test_the_order(self):
        lines = src("site", "app", "forecast", "lines.tsx")
        block = lines[lines.index("export function FilingCheck("):lines.index('data-fc-filing-fold={k}')]
        self.assertLess(block.index('key: "sound"'), block.index('{ key: "every", cells: ["Every month"'))
        self.assertIn("on the months whose operator filing passes the check and on every month", block)

    def test_the_drawn_page_and_the_note(self):
        self.assertIn("ready branch wip/ready-forecast-filing-sound-first", src("site", "scripts", "test-forecast-lines.mjs"))
        self.assertIn("leads with the scores on the months that pass and puts every month second", src("docs", "methods", "predict.md"))


if __name__ == "__main__":
    unittest.main()
