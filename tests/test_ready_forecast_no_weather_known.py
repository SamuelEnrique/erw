"""Ready branch for /forecast (session 11408, chain 770 part C; weekend page 2026-11-28, part 3.5, "the line 'with the
weather known (not a forecast)': keep, or remove"). Not the default: it waits for Samuel's ruling.

The other choice: the report card draws no table of the line (WEATHER_KNOWN_SHOWN in site/app/forecast/view.tsx); the
place files still carry it (all 64 places on the files now on main) and the report card's download still holds its rows,
marked as not a forecast. On main the line's table is drawn for every place that holds it (64), here for none.
site/scripts/test-forecast-peak.mjs (part 8) is turned to the same rule."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheWeatherKnownLineIsNotDrawn(unittest.TestCase):
    def test_the_switch(self):
        view = src("site", "app", "forecast", "view.tsx")
        self.assertIn("const WEATHER_KNOWN_SHOWN = false;", view)
        self.assertIn("{WEATHER_KNOWN_SHOWN && weathered ? (", view)
        self.assertEqual(view.count('data-fc-weather="1"'), 1)

    def test_the_note_and_the_drawn_page(self):
        self.assertIn('`/forecast` does not draw the line "with the weather known"', src("docs", "methods", "predict.md"))
        self.assertIn("ready branch wip/ready-forecast-no-weather-known", src("site", "scripts", "test-forecast-peak.mjs"))


if __name__ == "__main__":
    unittest.main()
